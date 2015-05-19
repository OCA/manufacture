Real costs in manufacturing orders
==================================

This module allows to manage the control of Manufacturing Orders actual costs,
by creating analytic lines as defined in the MO (from *mrp_project_link*).

It also updates product standard price when a manufacturing orders is finished
according this formula:

(Product stock * Product standard price + Production real cost) /
(Product stock + Final product quantity)
