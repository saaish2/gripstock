"""Rental order service — turns a confirmed reservation into a priced order."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.config import get_settings
from app.enums import OrderStatus, ReservationStatus
from app.errors import BusinessRuleError, ConflictError, NotFoundError
from app.models.order import OrderLine, RentalOrder
from app.pagination import Page, PageParams, paginate
from app.repositories.catalog import AssetRepository, KitRepository
from app.repositories.customer import CustomerRepository
from app.repositories.order import OrderRepository
from app.repositories.reservation import ReservationRepository
from app.services.audit import record_audit
from app.services.pricing import AssetRates, build_quote
from app.services.references import next_order_reference


class OrderService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.repo = OrderRepository(session)
        self.reservations = ReservationRepository(session)
        self.assets = AssetRepository(session)
        self.customers = CustomerRepository(session)
        self.kits = KitRepository(session)

    def create_from_reservation(
        self,
        reservation_id: int,
        tax_rate: Decimal = Decimal("0"),
        actor_id: int | None = None,
    ) -> RentalOrder:
        reservation = self.reservations.get(reservation_id)
        if reservation is None:
            raise NotFoundError(f"reservation {reservation_id} not found")
        if reservation.status not in (
            ReservationStatus.CONFIRMED,
            ReservationStatus.PICKED_UP,
        ):
            raise BusinessRuleError(
                "an order can only be drafted from a confirmed reservation"
            )
        if self.repo.for_reservation(reservation_id) is not None:
            raise ConflictError("an order already exists for this reservation")

        customer = self.customers.get(reservation.customer_id)
        if customer is None:
            raise NotFoundError("reservation customer no longer exists")

        asset_ids = [line.asset_id for line in reservation.lines]
        assets = {a.id: a for a in self.assets.list_by_ids(asset_ids)}
        rate_cards = [
            AssetRates(
                asset_id=a.id,
                daily_rate=a.daily_rate,
                weekly_rate=a.weekly_rate,
                monthly_rate=a.monthly_rate,
                replacement_value=a.replacement_value,
            )
            for a in assets.values()
        ]
        quote = build_quote(
            rate_cards,
            reservation.starts_at,
            reservation.ends_at,
            settings=self.settings,
            customer_discount=customer.discount_rate,
        )

        order = RentalOrder(
            reference=next_order_reference(self.session),
            customer_id=customer.id,
            reservation_id=reservation.id,
            status=OrderStatus.DRAFT,
            starts_at=reservation.starts_at,
            ends_at=reservation.ends_at,
        )
        for priced in quote.lines:
            asset = assets[priced.asset_id]
            order.lines.append(
                OrderLine(
                    asset_id=asset.id,
                    description=asset.name,
                    quantity=1,
                    rental_days=priced.rental_days,
                    unit_rate=priced.base_rate,
                    line_subtotal=priced.seasonal_rate,
                    discount_amount=priced.discount_amount,
                    deposit_amount=priced.deposit_amount,
                )
            )
        net = quote.net_total
        order.tax_total = (net * tax_rate).quantize(Decimal("0.01"))
        order.recalculate_totals()
        self.repo.add(order)
        record_audit(
            self.session,
            actor_id=actor_id,
            action="order.created",
            entity_type="order",
            entity_id=order.id,
            payload={"reference": order.reference, "grand_total": str(order.grand_total)},
        )
        return order

    def get(self, order_id: int) -> RentalOrder:
        order = self.repo.get(order_id)
        if order is None:
            raise NotFoundError(f"order {order_id} not found")
        return order

    def open(self, order_id: int) -> RentalOrder:
        order = self.get(order_id)
        if order.status != OrderStatus.DRAFT:
            raise BusinessRuleError("only draft orders can be opened")
        order.status = OrderStatus.OPEN
        self.session.flush()
        return order

    def close(self, order_id: int) -> RentalOrder:
        order = self.get(order_id)
        if order.status != OrderStatus.OPEN:
            raise BusinessRuleError("only open orders can be closed")
        order.status = OrderStatus.CLOSED
        self.session.flush()
        return order

    def cancel(self, order_id: int) -> RentalOrder:
        order = self.get(order_id)
        if order.status == OrderStatus.CLOSED:
            raise BusinessRuleError("closed orders cannot be cancelled")
        order.status = OrderStatus.CANCELLED
        self.session.flush()
        return order

    def search(
        self,
        params: PageParams,
        customer_id: int | None = None,
        status: OrderStatus | None = None,
    ) -> Page:
        stmt = self.repo.search_query(customer_id, status)
        return paginate(self.session, stmt, params)
