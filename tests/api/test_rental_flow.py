"""End-to-end API test of the full rental lifecycle."""

from __future__ import annotations

from datetime import datetime, timedelta


def _window(days_ahead=1, length=3):
    start = datetime(2025, 5, 1, 9, 0) + timedelta(days=days_ahead)
    end = start + timedelta(days=length)
    return start.isoformat(), end.isoformat()


def _reservation(client, headers, customer_id, asset_ids):
    starts_at, ends_at = _window()
    return client.post(
        "/reservations",
        json={
            "customer_id": customer_id,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "lines": [{"asset_id": aid} for aid in asset_ids],
        },
        headers=headers,
    )


def test_full_lifecycle(client, auth_headers, sample_catalog, sample_customer):
    asset_a = sample_catalog["asset_a"]["id"]
    asset_b = sample_catalog["asset_b"]["id"]
    customer_id = sample_customer["id"]

    # Reserve
    res = _reservation(client, auth_headers, customer_id, [asset_a, asset_b])
    assert res.status_code == 201, res.text
    reservation_id = res.json()["id"]
    assert res.json()["status"] == "pending"

    # Confirm
    confirmed = client.post(f"/reservations/{reservation_id}/confirm", headers=auth_headers)
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"

    # Create order from reservation
    order = client.post(
        "/orders",
        json={"reservation_id": reservation_id, "tax_rate": "0.08"},
        headers=auth_headers,
    )
    assert order.status_code == 201, order.text
    order_body = order.json()
    assert order_body["grand_total"] is not None
    assert len(order_body["lines"]) == 2

    # Generate + issue invoice
    invoice = client.post(f"/invoices/from-order/{order_body['id']}", headers=auth_headers)
    assert invoice.status_code == 201
    invoice_id = invoice.json()["id"]
    issued = client.post(f"/invoices/{invoice_id}/issue", headers=auth_headers)
    assert issued.json()["status"] == "issued"
    total = issued.json()["total"]

    # Pay in full
    payment = client.post(
        f"/invoices/{invoice_id}/payments",
        json={"amount": total, "method": "card"},
        headers=auth_headers,
    )
    assert payment.status_code == 201
    final = client.get(f"/invoices/{invoice_id}", headers=auth_headers)
    assert final.json()["status"] == "paid"


def test_checkout_and_checkin(client, auth_headers, sample_catalog, sample_customer):
    asset_a = sample_catalog["asset_a"]["id"]
    res = _reservation(client, auth_headers, sample_customer["id"], [asset_a])
    reservation_id = res.json()["id"]
    client.post(f"/reservations/{reservation_id}/confirm", headers=auth_headers)

    checkout = client.post(
        f"/operations/reservations/{reservation_id}/checkout",
        json=[{"asset_id": asset_a, "condition": "good"}],
        headers=auth_headers,
    )
    assert checkout.status_code == 200
    assert checkout.json()["status"] == "picked_up"

    checkin = client.post(
        f"/operations/reservations/{reservation_id}/checkin",
        json=[{"asset_id": asset_a, "condition": "good"}],
        headers=auth_headers,
    )
    assert checkin.status_code == 200
    assert checkin.json()["status"] == "returned"

    # Asset is available again
    asset = client.get(f"/assets/{asset_a}", headers=auth_headers)
    assert asset.json()["status"] == "available"
