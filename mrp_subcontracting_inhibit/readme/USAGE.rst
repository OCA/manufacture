#. Go to *Inventory > Configuration > Routes* and edit 'Buy' rule and check 'Subcontracting inhibit'.
#. Go to *Inventory > Products > Product* and create some product called 'Subcontract product'.
#. Go to *Inventory > Products > Product* and create other product called 'Component'.
#. Go to *Manufacturing > Products > Bill of materials* and create a new one with type = "Subcontracting" related to 'Subcontract product' and set 'Component' product.
#. Go to *Inventory > Products > Product* and edit 'Subcontract product' and set Purchase tab as follows:
#. [Vendor line 1] Vendor: Azure Interior, Subcontracting inhibited: Yes, Price: 5.
#. [Vendor line 2] Vendor: Azure Interior, Subcontracting inhibited: No, Price: 10.


Purchase order flow:
#. Go to *Purchase > Orders > Requests for Quotation* and create new order as follows:
#. Vendor: Azure Interior, Product: Subcontract product
#. The unit price of the product will be 10.
#. Click on the 'Confirm Order' button.
#. A production order will have been created.

Replenishment flow:
#. Go to *Inventory > Products > Product* and go to 'Subcontract product'.
#. Click on the 'Replenish' button, select 'Buy' in Preferred Routes field and click on the 'Confirm' button.
#. A new purchase order will have been created, go to *Purchase > Orders > Requests for Quotation* and enter it.
#. The unit price of the product will be 5.
#. Click on the 'Confirm Order' button.
#. A production order will not have been created.
