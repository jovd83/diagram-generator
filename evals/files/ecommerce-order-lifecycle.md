# Ecommerce Order Lifecycle

Model the lifecycle of a single order.

States:

- Draft
- Submitted
- PaymentAuthorized
- Packing
- Shipped
- Delivered
- Cancelled
- Returned
- Refunded

Transitions:

- `Draft -> Submitted` when the customer confirms checkout
- `Submitted -> PaymentAuthorized` when the payment provider authorizes the charge
- `Submitted -> Cancelled` when the customer cancels before authorization
- `PaymentAuthorized -> Packing` when inventory is reserved
- `PaymentAuthorized -> Cancelled` when inventory reservation fails and the payment is released
- `Packing -> Shipped` when the carrier scans the parcel
- `Shipped -> Delivered` on proof of delivery
- `Delivered -> Returned` when the customer opens a return
- `Returned -> Refunded` after warehouse inspection approves the refund

Guidance:

- Keep the diagram readable.
- Do not model retries or rare exceptions unless they are essential.
