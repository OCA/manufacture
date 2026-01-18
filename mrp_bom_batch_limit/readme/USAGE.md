1. **Configure BoM**: Edit a BoM and enable batch limits with min/max quantities
2. **Create Production Order**: Create a manufacturing order with the configured BoM
3. **Warning Banner**: If quantity is outside limits, a warning banner appears in draft state
4. **Confirmation Blocked**: Trying to confirm the order will show an error message

Example Workflow:

If a product has a BoM with:
- Min Batch Quantity: 5 units
- Max Batch Quantity: 20 units
- Enable Batch Limit: True

Production Order Behavior:
- Quantity 3 units: Shows warning "Quantity (3.00) is below minimum batch quantity (5.00)"
- Quantity 10 units: No warning (within limits)
- Quantity 25 units: Shows warning "Quantity (25.00) exceeds maximum batch quantity (20.00)"

Validation:
- Draft MO with invalid quantity: Warning banner visible
- Attempt to confirm invalid MO: Error message blocks confirmation
- Valid quantity: Normal confirmation process
