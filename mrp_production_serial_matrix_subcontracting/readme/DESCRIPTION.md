Extends `mrp_production_serial_matrix` to support Odoo subcontracting flows.

A *Serial Numbers Matrix* button is added to the receipt transfer for
subcontracted products tracked by serial number, so the user can fill the
component lots/serials matrix without having to open the subcontracting
record-components modal first.

When the matrix finishes processing (either successfully or with an error),
the user who launched it is notified with a message posted on the
subcontracting receipt.
