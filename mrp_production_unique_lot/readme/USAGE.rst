1. **Configuring The Operation Type**

   - Navigate to Inventory > Configuration > Operation Types.
   - Open the Manufacturing operation type.
   - Check the option 'Force Production Lot Uniqueness'.

2. **Creating a Manufacturing Order**

   - Create an MO for a product that is tracked by lots.
   - Assign an existing **lot number** for the finished product. This should be a lot number
     used on a done production.

3. **Validating the Manufacturing Order**

   - When you validate the MO, an error is thrown because the lot has already been produced.

