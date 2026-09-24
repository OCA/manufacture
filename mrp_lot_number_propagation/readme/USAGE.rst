=====
Usage
=====


To configure lot number propagation for a specific product:

#. Go to *Manufacturing > Products > Bill of Materials*
#. Select or create a BOM
#. In the BOM form, check the "Propagate Lot" checkbox
#. Select a single component from the BOM lines from which the lot number will be propagated to the finished product
#. The final product and the selected component must have lot/serial number tracking enabled


When the selected component with lot tracking is used in a manufacturing order:

#. When consuming the selected component with a lot number, the system will automatically propagate that lot number to the manufactured product.
#. Only the lot number from the specifically selected component in the BOM will be propagated to the finished product.
#. The propagation is made by generation a new lot/serial number for the final product with the component lot/serial number information.

To view lot traceability:

#. Go to the manufactured product
#. Select the lot number to view its origin and related components
