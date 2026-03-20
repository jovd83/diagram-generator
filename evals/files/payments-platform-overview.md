# Payments Platform Overview

Goal: create a compact documentation bundle for a payments platform.

Components:

- Merchant Dashboard (React frontend)
- Partner Integrations
- API Gateway
- Payments Service
- Risk Service
- Ledger Service
- PostgreSQL
- Kafka
- External PSP

Key relationships:

- Merchant Dashboard and Partner Integrations both call the API Gateway.
- The API Gateway routes payment-intent requests to the Payments Service.
- The Payments Service asks the Risk Service for an approve or reject decision.
- The Payments Service calls the External PSP to authorize or capture funds.
- The Payments Service publishes payment events to Kafka.
- The Ledger Service consumes Kafka events and writes accounting records to PostgreSQL.
- The Payments Service stores operational payment data in PostgreSQL.

Desired outcome:

- Produce a small, high-value bundle rather than a giant all-in-one diagram.
- Cover system context, the core payment flow, and one structural or data-centric view.
