# API reference

All endpoints are JSON over HTTP. Except for `/health*` and `/auth/login`,
every request must carry a bearer token obtained from `POST /auth/login`.

Authorization is role-ranked: `viewer < agent < manager < admin`. The minimum
role for each endpoint is listed below.

## Auth

| Method | Path                    | Role    | Description                       |
|--------|-------------------------|---------|-----------------------------------|
| POST   | `/auth/login`           | —       | Exchange credentials for a token  |
| POST   | `/auth/logout`          | any     | Revoke the current session        |
| GET    | `/auth/me`              | any     | Current user profile              |
| POST   | `/auth/change-password` | any     | Rotate password, revoke sessions  |

## Users (admin)

| Method | Path           | Description          |
|--------|----------------|----------------------|
| POST   | `/users`       | Create a user        |
| GET    | `/users`       | List active users    |
| PATCH  | `/users/{id}`  | Update role/active   |

## Customers

| Method | Path                       | Role    | Description            |
|--------|----------------------------|---------|------------------------|
| POST   | `/customers`               | agent   | Create customer        |
| GET    | `/customers`               | agent   | Search + paginate      |
| GET    | `/customers/{id}`          | agent   | Fetch one              |
| PATCH  | `/customers/{id}`          | agent   | Update fields          |
| POST   | `/customers/{id}/status`   | manager | Change account status  |
| DELETE | `/customers/{id}`          | manager | Archive (soft delete)  |

## Catalog

| Method | Path                    | Role    | Description                 |
|--------|-------------------------|---------|-----------------------------|
| POST   | `/categories`           | manager | Create category             |
| GET    | `/categories`           | agent   | List                        |
| POST   | `/assets`               | manager | Create asset                |
| GET    | `/assets`               | agent   | Search (term/category/status) |
| PATCH  | `/assets/{id}`          | manager | Update asset                |
| POST   | `/assets/{id}/status`   | manager | Transition asset status     |
| DELETE | `/assets/{id}`          | manager | Soft delete                 |
| POST   | `/kits`                 | manager | Create kit (bundle)         |
| GET    | `/kits`                 | agent   | List active kits            |

## Reservations

| Method | Path                              | Role  | Description                  |
|--------|-----------------------------------|-------|------------------------------|
| POST   | `/reservations`                   | agent | Create (conflict-checked)    |
| POST   | `/reservations/availability`      | agent | Check a single asset window  |
| GET    | `/reservations`                   | agent | Search + paginate            |
| POST   | `/reservations/{id}/confirm`      | agent | Hold inventory               |
| POST   | `/reservations/{id}/cancel`       | agent | Release inventory            |
| POST   | `/reservations/{id}/reschedule`   | agent | Move window (re-checked)     |

## Orders & invoices

| Method | Path                              | Role  | Description                  |
|--------|-----------------------------------|-------|------------------------------|
| POST   | `/orders`                         | agent | Draft from reservation (idempotent) |
| GET    | `/orders`                         | agent | Search + paginate            |
| POST   | `/orders/{id}/open`               | agent | Open a draft order           |
| POST   | `/orders/{id}/close`              | agent | Close an open order          |
| POST   | `/invoices/from-order/{id}`       | agent | Generate an invoice          |
| POST   | `/invoices/{id}/issue`            | agent | Issue with net terms         |
| POST   | `/invoices/{id}/void`             | manager | Void an unpaid invoice     |
| POST   | `/invoices/{id}/payments`         | agent | Record a payment             |

## Operations

| Method | Path                                                  | Role    |
|--------|-------------------------------------------------------|---------|
| POST   | `/operations/reservations/{id}/checkout`              | agent   |
| POST   | `/operations/reservations/{id}/checkin`               | agent   |
| GET    | `/operations/reservations/{id}/inspections`           | agent   |
| POST   | `/maintenance`                                        | manager |
| PATCH  | `/maintenance/{id}`                                   | manager |

## Platform

| Method | Path              | Role  | Description                  |
|--------|-------------------|-------|------------------------------|
| POST   | `/webhooks`       | admin | Register endpoint            |
| POST   | `/api-keys`       | admin | Issue key (shown once)       |
| GET    | `/audit`          | manager | Recent audit entries       |
| GET    | `/reports/dashboard` | viewer | Ops dashboard             |

