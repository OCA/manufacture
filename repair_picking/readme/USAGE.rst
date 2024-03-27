Getting Started
===============

1. Install the module in your Odoo instance.

2. Navigate to Inventory > Configuration > Warehouses, and select a warehouse.

3. In the "Repair Steps" field, choose between "Repair", "Pick component, repair", or "Pick component, repair, store removed component" to define the repair process.

4. Define the "Repair Location", "Add Component to Repair" picking type, "Remove component from Repair" picking type, and "Repair Route" as needed.

Using the Repair Management Extension
=====================================

1. Navigate to Repair > Repair Orders and create a new repair order.

2. In the Operations tab, add components to be added or removed during the repair process.

3. Confirm the repair order. This will automatically generate the necessary pickings based on the configured repair steps.

4. Process the pickings as required during the repair process.

5. If the repair order needs to be canceled, all associated pickings that are not in "cancel" or "done" state will also be canceled automatically.
