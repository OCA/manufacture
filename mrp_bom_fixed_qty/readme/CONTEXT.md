In standard Odoo every BoM line scales proportionally with the quantity of the
manufacturing order. With this module, a line flagged as *Fixed Qty* keeps the
quantity written on the BoM, whatever the quantity to produce.

It applies to:

* **Components** (BoM lines): the quantity consumed is always the one on the
  line, for example one box or one label per order, or the material needed
  for a single sample.
* **By-products**: the quantity produced is always the one on the line, for
  example one quality-control sample per order.

When the quantity of a manufacturing order is changed with the *Change
Quantity* wizard, fixed component lines are left untouched.

This is really helpfull if we want to handle complex manufacturing process.

For example:

A company that packs products manufactures in batches of variable size. The
BoM is proportional, for example 1 kg of product for 6 packed units, and the
same BoM is used for any batch size (10 kg, 25 kg, and so on).

On every batch, one unit must be set aside for quality control. It is not for
sale, and it does not depend on the size of the batch: it is always one unit.

Two accounting requirements follow:

* The cost of the sample must not be lost or sent to a loss account (as a
  scrap would do). It must be absorbed by the units that are sold.
* The sample must be kept apart from the sellable stock, with no value of
  its own.

Standard Odoo cannot express this on the BoM:

* A by-product with a cost share of 0 % solves the cost, but its quantity
  scales with the order, so it has to be corrected by hand on every order.
* The material consumed by the sample is also a fixed amount, but component
  lines scale as well.

With this module the order is entered with the sellable quantity (for
example 60) and the BoM does the rest. The proportional lines consume the
material for 60 units, a fixed quantity adds the material for the
sample, and a by-product line using a fixed quantity with 0 % cost share produces the sample.
The main product therefore absorbs the full cost, divided by the sellable
units only.
