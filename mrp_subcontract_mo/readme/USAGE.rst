After creation of a Manufacturing Order (either manually or from Sale Order), a new button is displayed in the Manufacturing Order form **Subcontract Order**
When clicking on this button a wizards appears allowing you to select :
#. **Subcontractor** to whom this Manufacturing Order would be subcontracted
#. Associated **Service** that could be purchased from this Subcontractor to Manufacture the products

When clicking on **Subcontract** button on the wizard, pickings for delivery of raw materials, receipt of manufactured ones are created, together with Purchase Order for selected Service (if service was selected).

The existing Pickings button is updated to display all pickings related to this Manufacturing Order (including Purchase pickings for raw materials if applicable) and the number of completed ones.
An additional Purchases button is added to display all RFQ / Purchase Orders related to this Manufacturing Order (including Purchase Orders for raw materials if applicable) and the number of confirmed ones.
