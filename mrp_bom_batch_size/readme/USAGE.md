
1. **Configure BoM**: Edit a BoM and set the batch size
2. **Create Procurement**: Create a procurement or sales order that triggers manufacturing
3. **Automatic Splitting**: The system will create multiple manufacturing orders of the configured batch size
4. **Manual Splitting**: Use the production split wizard with pre-populated batch size

Example Workflow:

If a product has a BoM with:
- Batch Size: 10 units
- Enable Batch Size: True

A procurement for 25 units will create:
- Manufacturing Order 1: 10 units
- Manufacturing Order 2: 10 units  
- Manufacturing Order 3: 5 units

Production Split Wizard:

The enhanced production split wizard automatically:
- Displays the BoM's batch size as the maximum batch size
- Calculates the number of splits needed
- Pre-populates split quantities based on batch size

Access the wizard from:
- Manufacturing Order form view: "Split" button
- Manufacturing Order list view: "Split" action menu
