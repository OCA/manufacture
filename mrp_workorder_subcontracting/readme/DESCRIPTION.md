Odoo standard subcontracting is mainly managed from the manufacturing order
and product routes. This module adds subcontracting at work order level, so a
company can outsource only specific operations of a manufacturing order while
keeping the other operations internal.

The module is useful when a production process is split into several work
orders and only some of them must be sent to an external supplier. For each
subcontracted work order, the user can manage the related supplier, purchase
document and stock transfers without losing the link with the original
manufacturing order.

It extends manufacturing operations, work orders, purchase orders and stock
moves to provide:

- Subcontracting configuration on routing operations, copied to generated work
  orders;
- A wizard to create the subcontracting documents for the remaining quantity of
  one or more work orders;
- A standard purchase flow based on RFQs and purchase orders;
- A bidding flow where several suppliers can quote the same subcontracted work
  order and one purchase order is confirmed as the winner;
- Urgent flows to send goods to a subcontractor before a purchase order is
  required;
- Flows for goods that are already available at the subcontractor location;
- Traceability between manufacturing orders, work orders, purchase order lines
  and stock moves;
- Automatic work order completion when the expected subcontracting receipt is
  validated.
- Track what's in stock for each supplier, including items that have been shipped and those still to be received
