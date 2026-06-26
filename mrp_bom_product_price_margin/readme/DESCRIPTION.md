Help handling cost and sale price of product template linked to bill of
material.

This module computes a **BoM Unit Cost** from the components of a Bill
of Material, compares it to the product's standard price and sale price,
and highlights negative margins (it relies on `product_standard_margin`
for the margin computation). A button lets you apply the computed BoM
cost to the product's standard price.

It also adds a **Cost basis** on each Bill of Material, letting you
choose how the BoM Unit Cost is computed:

- **Direct (this BoM level only)**: sum of the components' own cost
  (standard price), for this level only. Use it when you maintain costs
  bottom-up, updating each level yourself.
- **Rolled-up (sub-BoMs + operations)**: recurse through sub-BoMs and
  add operation / work-center costs in one pass. Components without a
  BoM fall back to their standard price, so it reconciles with Direct
  once all sub-costs are maintained.
