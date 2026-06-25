1.  Open a Bill of Materials (*Manufacturing \> Products \> Bills of
    Materials*).
2.  The **BoM Cost** and **BoM Unit Cost** fields show the rolled-up
    cost, recomputed live as component costs or the BoM change.
3.  Click **Set Product Cost from BoM** in the BoM header to write the
    BoM Unit Cost into the produced product's cost. The action is
    restricted to the *Manufacturing / Administrator* group.
4.  Alternatively, from a product with a BoM, use the **Cost from BoM**
    button in the product's button box.

Notes:

- Component costs are read from each component's `standard_price` and
  converted into the component's reference unit of measure.
- Sub-assemblies (BoM lines that have their own BoM) are rolled up
  recursively, so multi-level structures are fully costed.
- Operation cost uses the operation's *manual duration* and the work
  center's *cost per hour*; operations without an hourly cost are
  ignored.
- Writing the rolled-up cost into `standard_price` is most meaningful
  for products using the *standard* costing method. Under *average* or
  *FIFO* costing, Odoo recomputes the cost from inventory moves, so a
  value written here may be overwritten on the next valuation.
