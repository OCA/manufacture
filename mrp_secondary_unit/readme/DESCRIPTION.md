This module allows to express manufacturing quantities in a secondary unit, in
the same way as `sale_order_secondary_unit` and `purchase_order_secondary_unit`
do for sales and purchases.

Secondary units are added to:

- the bill of materials quantity, its component lines and its by-product lines,
- the manufacturing order quantity to produce, its components and its
  by-products.

The secondary unit of a component is taken from the bill of materials, so the
components of a manufacturing order come already expressed in the unit the
recipe was written in, without any manual encoding.
