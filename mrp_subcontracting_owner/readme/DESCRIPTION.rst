This module does the following:

- Passes the Assign Owner (owner_id) value of picking of the subcontracting move to the
  generated manufacturing order.
- Excludes subcontracting receipt moves from the 'Standard Behavior' scope of the owner
  restriction setting, practically making those moves behave in the 'Picking Partner'
  way, since the picking type of the subcontracting receipt is usually the normal
  incoming receipt which does not assume a receipt from another internal location, and
  therefore is inconvenient to set the owner restriction as 'Picking Partner'.

This module depends on the following OCA modules:

* mrp_stock_owner_restriction
* purchase_order_owner
