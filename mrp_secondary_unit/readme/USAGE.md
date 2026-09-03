Define the secondary units of a product in the *Secondary Unit of Measure*
section of its *General Information* tab, then:

On a bill of materials, pick a *Second unit* on the quantity to produce, on a
component line or on a by-product line and enter the *Secondary Qty*. The
quantity in the primary unit is computed from it, so a recipe can be written as
"2 boxes of 10 units" and stored as 20 units.

Picking the unit alone never changes a quantity that is already there: the
secondary quantity is derived from it, and only a secondary quantity that is
entered afterwards drives the quantity in the primary unit.

When a manufacturing order is created from that bill of materials, the secondary
unit of each component is copied to the corresponding component line, and the
secondary quantity is derived from the quantity to consume that Odoo explodes
from the bill of materials. Changing the quantity to produce rescales both
quantities.

Component and by-product lines of a manufacturing order can also be encoded in
the secondary unit directly: entering a *Secondary Qty* recomputes the quantity
in the primary unit.

Note that only secondary units whose dependency type is *Dependent* are
propagated to the generated component and by-product lines, as an *Independent*
secondary quantity cannot be derived from the primary quantity.
