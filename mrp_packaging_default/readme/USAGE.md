Some component products must exist. Those components will be later included in the manufactured or kit product. Then, you'll notice the module effects.

To create the component products:

1. Go to *Inventory > Products > Products*.
2. Create a product.
3. Configure its unit of measure (if you enabled that option).
4. Add some line(s) in *Inventory > Packaging*.

To use this module with **a kit of products**, you need to:

1. Go to *Inventory > Products > Products*.
2. Create a product that will be the kit.
3. Set *Product Type* "Consumable".
4. Configure its unit of measure (if you enabled that option).
5. Enable *Inventory > Operations > Routes > Manufacture*.
7. Click on *Bill of Materials* button and create a new one.
8. Set *BoM Type* "Kit".
9. Configure the rest of the BoM. When you configure the component lines, use
   the new *Packaging* and *Packaging Qty* fields.
10. Go to *Inventory > Delivery Orders (three dots) > New > Planned Transfer*.
11. Fill the *Delivery Address*.
12. Add one *Operations* line with the kit product you just created.
13. Click on *Mark as TODO*.
14. You will notice that the kit has been replaced by its components, and each
    component line includes the packaging and its qty, just like you configured
    them in the BoM.

To use it with **a manufactured product**, instead:

1. Go to *Inventory > Products > Products*.
2. Create a product; the one that will be manufactured.
3. Set *Product Type* "Storable Product".
4. Configure its unit of measure (if you enabled that option).
5. Enable *Inventory > Operations > Routes > Manufacture*.
7. Click on *Bill of Materials* button and create a new one.
8. Set *BoM Type* "Manufacture this product".
9. Configure the rest of the BoM. When you configure the component lines, use
   the new *Packaging* and *Packaging Qty* fields.
10. Go back to the product form.
11. Click on *Reordering Rules* button and create a new one.
12. Set some minimal and maximal quantities.
13. Click on *Order Once*. If you don't see this button, you can also go to
    *Inventory > Operations > Run Scheduler > Run Scheduler*.
14. Go to *Manufacturing > Operations > Manufacturing Orders*. You will see a
    new MO created from the reordering rule. Open it.
15. See how the *Components* lines contain packaging information, just like you
    defined it in the BoM. The same would happen if you created the MO
    manually.
