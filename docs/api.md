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

