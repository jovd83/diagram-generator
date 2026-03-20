# Order Domain ERD Source

Goal: provide a compact, grounded source note for an order-domain ER diagram example.

Entities:

- CUSTOMER
  - id (PK)
  - email
  - full_name
- ORDER
  - id (PK)
  - customer_id (FK -> CUSTOMER.id)
  - status
  - submitted_at
  - total_amount
- ORDER_ITEM
  - id (PK)
  - order_id (FK -> ORDER.id)
  - sku
  - quantity
  - unit_price
- PAYMENT
  - id (PK)
  - order_id (FK -> ORDER.id)
  - provider_reference
  - status
  - authorized_at
- SHIPMENT
  - id (PK)
  - order_id (FK -> ORDER.id)
  - carrier
  - tracking_number
  - shipped_at
- RETURN_REQUEST
  - id (PK)
  - order_id (FK -> ORDER.id)
  - created_at
  - status

Relationships:

- A CUSTOMER places many ORDER records.
- An ORDER contains many ORDER_ITEM records.
- An ORDER can have multiple PAYMENT attempts.
- An ORDER can have zero or one SHIPMENT.
- An ORDER can have zero or one RETURN_REQUEST.
