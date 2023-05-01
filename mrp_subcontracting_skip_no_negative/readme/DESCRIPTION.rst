This module skips the negative quantity check, provided by stock_no_negative, for
subcontracting receipts.

Background:
~~~~~~~~~~~

Odoo processes subcontracting receipt in the order of:

1. Transfer of the subcontracted product from the subcontractor location to the internal
location.
2. Production of the subcontracted product in the subcontractor location.

This sequence does not represent the reality where production is done before transfer, and therefore
the above Step 1 would fail with negative stock in the subcontractor location, when stock_no_negative
is installed, unless the product/location is configured to allow negative stock.

ref. https://github.com/odoo/odoo/pull/75065
