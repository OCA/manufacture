In some processes the components are issued for the planned quantity of a
manufacturing order and the yield is not exact: the order plans 1,000 units,
the material for 1,000 units is consumed, but only 998 good units come out.

When the produced quantity is registered on the manufacturing order, Odoo
scales the consumed quantity of every component down to the produced
quantity, so the material lost in the process stays in stock and the user has
to correct the consumption of each component by hand. When the bill of
materials is set to block or warn about consumption differences, Odoo also
compares the consumption with the quantity scaled by the produced quantity.

This module adds a *Fixed Consumption* option to the bill of materials. On
the manufacturing orders of such a bill, registering a produced quantity
keeps the consumption of the components at the planned quantity, and the
consumption check compares with the planned quantity as well. Components
whose consumption was registered by hand are kept as they are, as in the
standard flow.
