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

