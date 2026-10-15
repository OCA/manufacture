### MRP Areas

Go to *Manufacturing > Configuration > MRP Areas* and define one area
per stock location you want to plan independently. Each area requires:

- **Warehouse**: the warehouse the area belongs to. Working hours are
  taken from the warehouse calendar (see `mrp_warehouse_calendar`).
- **Location**: the stock location whose on-hand quantity and moves are
  planned.

A default `WH/Stock` area is created on installation.

### Product MRP Area Parameters

For a product to be planned in an area, it needs a *Product MRP Area
Parameters* record:

- Go to *Manufacturing > Products > Product MRP Area Parameters*, or
- open the product form and use the **MRP Areas** smart button.

Relevant parameters:

- **Safety Stock**: minimum quantity the planner keeps on hand.
  *Example: with a safety stock of 10, the run proposes replenishment
  as soon as the projected stock would drop below 10 units.*
- **Minimum / Maximum Order Qty**: bounds applied to each proposed
  order. *Get from main supplier* copies the vendor's minimum quantity.
- **Qty Multiple**: rounds the ordered quantity up to a multiple.
  *Example: a requirement of 47 units with Qty Multiple = 20 and
  Maximum Order Qty = 40 is planned as two orders of 40 and 20.*
- **Nbr. Days**: groups demand within this many days into a single
  planned order (`0` plans every demand separately). *Example: with
  Nbr. Days = 7, demands of 5 units on Monday and 7 units on Thursday
  are covered by one planned order of 12 units.*
- **Procure Location**: alternative child location to procure into
  (defaults to the area's location). *Example: plan the `WH/Stock` area
  but have purchased goods delivered to `WH/Stock/Incoming`.*
- **Exclude from MRP**: skips the product in the calculation.
- **MRP Planner**: used by the "My products" filters.
- **Distribution Lead Time**: lead time for pull/push supply methods.

The **Supply Method** (Buy, Produce, Kit, Pull From, Push To, Pull &
Push) and **Main Supplier** are computed automatically from the
product's routes, bills of material and vendor pricelists. The **Lead
Time** is taken from the BoM manufacturing lead time, the main
supplier's delivery delay or the distribution lead time. *Example: a
purchase proposal due on Friday with a vendor delay of 3 days gets an
order release date on Tuesday — or earlier if the warehouse working
hours do not cover every day of the week.*

### Security groups

- **Run MRP Manually**: grants access to *Manufacturing > Planning >
  Run MRP Multi Level*.
- **Change procure quantity in MRP**: allows editing quantities in the
  procurement wizard (otherwise quantities are read-only).

### Scheduled action

The *Multi Level MRP* cron runs daily for all areas. Adjust it under
*Settings > Technical > Automation > Scheduled Actions*.

### Other settings

- The system parameter `mrp_multi_level.llc_calculation_recursion_limit`
  (default `1000`) bounds the low level code calculation; raise it for
  very deep BoM structures.
- Make sure products have the proper routes, BoMs and vendor
  pricelists (with delivery lead times) configured.
