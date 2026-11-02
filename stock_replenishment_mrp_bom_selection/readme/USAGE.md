1. Go to "Inventory / Operations / Replenishment"
2. Create or use a record with the "Manual" trigger whose product is
   manufactured (either with the manufacturing route set explicitly, or
   resolved by default because the product has bills of materials).
3. Click on the "Order" button of the line, and the wizard should open.
4. Optionally use the information icon of each line to check the on hand
   quantity of the raw materials of that bill of materials.
5. Set the quantity you want to produce with each bill of materials. The
   pending quantity is shown as "Quantity Remaining to Produce".
6. On confirmation, one manufacturing order per filled line will be created,
   and the remaining quantity will stay in the replenishment record.

Automatically triggered records are not affected: they keep the standard
Odoo behavior, as their quantity to order is always the computed one.
