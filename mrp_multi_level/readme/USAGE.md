### How it works

Each MRP run performs the following steps:

1. **Cleanup** – removes previous MRP moves, MRP inventory records and
   non-fixed planned orders.
2. **Low Level Code calculation** – computes the lowest BoM level each
   product appears at.
3. **Applicability** – flags which product/area parameters participate
   in the run (storable goods, not excluded).
4. **Initialisation** – collects demand and supply into *MRP Moves*
   from open stock moves, unconfirmed purchase orders and any forecast
   source provided by extension modules.
5. **Calculation** – nets demand against stock level by level,
   respecting safety stock, ordering constraints and lead times, and
   creates Planned Orders.
6. **Final process** – builds the time-phased MRP Inventory projection.

### Running the MRP scheduler

To run manually:

1. Go to *Manufacturing > Planning > Run MRP Multi Level* (requires the
   *Run MRP Manually* group).
2. Optionally select specific **MRP Areas to run**; leave empty to run
   all areas.
3. Click *Run MRP*. You are redirected to the MRP Inventory view.

The *Multi Level MRP* scheduled action runs the same calculation daily.

*Example end-to-end flow (with the demo data installed): a confirmed
sales order for 10 units of FP-2 creates demand at the top level. After
the run, Planned Orders show a proposal to manufacture 10 FP-2, plus
proposals for its components SF-1 and SF-2, and purchase proposals for
the components PP-1 and PP-2 further down. Filtering MRP Inventory by
*To Procure* and running *Procure* turns them into draft manufacturing
and purchase orders.*

### Reviewing the results

- *Manufacturing > Planning > MRP Inventory* shows the time-phased
  projection per product and day: starting inventory, demand, supply
  (including unconfirmed RfQs), forecasted inventory, quantity to
  procure and the order release date. Filter with **To Procure** to see
  where action is needed.
- *Manufacturing > Planning > Planned Orders* lists the proposed
  orders. Non-fixed orders (highlighted) are recalculated on the next
  run; use *Action > Toggle Fixed* to freeze an order so it survives
  subsequent runs. Orders created manually are fixed by default.

### Releasing planned orders

From the MRP Inventory list, or from Planned Orders:

1. Select the records and click **Procure** (or the per-row button).
2. In the wizard, review quantities, dates and destinations — editable
   quantities require the *Change procure quantity in MRP* group.
3. Click *Execute*. A procurement is run for each line, creating a
   draft purchase order, manufacturing order or stock transfer
   according to the product's routes, and the released quantity is
   tracked on the planned order. *Example: releasing a Produce planned
   order of 10 units creates a draft MO for 10 units and the planned
   order's released quantity becomes 10.*
