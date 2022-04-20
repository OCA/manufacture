Subcontracting Picking
~~~~~~~~~~~~~~~~~~~~~~

Currently when a Purchase Order for subcontracted product(s) is confirmed it automatically creates
a picking in the "Ready" state.
However this might be misleading because the goods are being manufactured by the subcontractor
and are not available immediately upon the PO confirmation.

This module introduces a new "Subcontracted" state for the Stock Picking created for the subcontracted products.

This state is technically the same as the "Draft" but allows to distinguish pickings for the goods being currently
manufactured by the subcontractor.
