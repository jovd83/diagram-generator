# Authentication Incident Timeline

Goal: capture the grounded failure path during a production degradation incident.

Participants:

- User
- Web App
- API Gateway
- Auth Service
- PostgreSQL
- Pager / Alerting

Timeline:

1. The user submits a login request in the Web App.
2. The Web App sends the request to the API Gateway.
3. The API Gateway forwards the request to the Auth Service.
4. The Auth Service attempts to load the user record from PostgreSQL.
5. PostgreSQL responds slowly because the primary is saturated.
6. The Auth Service hits its database timeout budget and returns an authentication service error to the API Gateway.
7. The API Gateway returns a 503-style failure response to the Web App.
8. Alerting triggers because timeout and error-rate thresholds are breached.

Guidance:

- Focus on the failure path, not the recovery work.
- Do not invent retries, caches, or failover behavior that are not described here.
- If any assumption is needed for diagram readability, mark it explicitly.
