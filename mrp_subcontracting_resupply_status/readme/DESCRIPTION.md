This module adds more visibility of the resupply transfer status for
subcontracting purchases and receipts.

- Adds a field in purchase orders resupply_status, to know the status of
  the resupply transfers if any.
- Adds a field in receipts transfers resupply_status, to know the status
  of the resupply transfer that precedes the receipt, if any.

In Odoo 20.0 the subcontractor resupply is configured on the warehouse
("Resupply Subcontractors") and the "Resupply Subcontractor on Order"
route is not selectable on products by default, so the module now detects
the resupply transfers from the subcontracting manufacturing order and
their subcontracting destination location instead of the product routes.
