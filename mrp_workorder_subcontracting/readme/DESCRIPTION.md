Standard subcontracting flows in Odoo are managed at manufacturing order
level. This module adds subcontracting management at workorder level, so
only selected operations of a manufacturing order can be outsourced.

It extends routing operations, workorders, purchase orders and stock
transfers to provide:

- subcontracting flags, allowed subcontractors and service products on
  routing operations, automatically copied to generated work orders;
- a workorder wizard to create subcontracting documents for the selected
  remaining quantity;
- a standard purchase flow that creates RFQs or reuses a draft purchase
  order, then generates the outgoing and incoming subcontracting transfers;
- a bidding flow where several subcontractors receive competing RFQs and
  the confirmed purchase order becomes the winning bid;
- urgent subcontracting flows that create direct outgoing transfers without
  requiring a purchase order first;
- subcontractor-stock flows for cases where the processed goods are already
  available from the subcontractor side;
- traceability between manufacturing orders, work orders, purchase order
  lines and stock moves;
- automatic work order completion when the expected subcontracting receipt
  is completed.
