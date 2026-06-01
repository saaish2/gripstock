# API reference

All endpoints are JSON over HTTP. Except for `/health*` and `/auth/login`,
every request must carry a bearer token obtained from `POST /auth/login`.

Authorization is role-ranked: `viewer < agent < manager < admin`. The minimum
role for each endpoint is listed below.

