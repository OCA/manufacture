Configure the subcontracting master data:

1. Go to the routing operation that can be outsourced.
2. Enable **Subcontract**.
3. Set the allowed subcontractors and the subcontracting service product.
4. Configure subcontracting picking types on the warehouse and on the
   subcontracting purchase order type.
5. Optionally configure subcontract and virtual subcontract locations on the
   supplier.

When a manufacturing order creates its work orders, the subcontracting
configuration is copied from the routing operation to each work order. It can
still be adjusted on the work order until subcontracting documents are created.

To subcontract work orders:

1. Open or select one or more work orders.
2. Run **Create Subcontract Order** from the work order action menu.
3. Select the supplier or suppliers, scheduled date, service product and flow
   type.
4. Confirm the wizard.

Available flow types:

- **Standard**: creates a purchase order line on a new RFQ or on an existing
  draft RFQ. When the purchase order is confirmed, the module creates the
  outgoing subcontracting transfer and then the incoming transfer. If the
  purchase order type enables immediate return, the incoming transfer is
  prepared immediately at purchase confirmation.
- **Urgent**: creates the outgoing transfer directly, without requiring a
  purchase order first. The user must provide an urgency reason, which is
  posted on the manufacturing order. A purchase order can still be linked when
  only one supplier is selected.
- **Subcontractor stock**: creates the incoming transfer for processed goods
  supplied from the subcontractor side. A purchase order can also be linked
  when only one supplier is selected.

If several suppliers are selected, the wizard automatically forces the
standard flow and creates one RFQ per supplier. Confirming one RFQ opens a
winning bid confirmation wizard. After confirmation, competing RFQs are either
cancelled or their losing lines are set to zero and locked.

The module adds smart buttons and document links on manufacturing orders,
purchase orders and stock pickings. Work orders also show subcontracting
status, purchase lines, delivery moves and return moves.

When the incoming subcontracting transfer is validated, the related work order
is evaluated. If a received quantity is available, the work order is completed
for that quantity. If no valid receipt is found after the logistics documents
are closed, the work order is marked with a subcontracting exception.
