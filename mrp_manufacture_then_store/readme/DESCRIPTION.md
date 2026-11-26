Add a warehouse manufacturing configuration that consumes components directly
from Stock and produces finished goods in Post-Production. A separate internal
transfer stores the finished goods in Stock.

The storage transfer is created when manufacturing finishes, as in Odoo's
standard three-step manufacturing flow. It stays linked to the manufacturing
output and follows standard stock move reservation and backorder behavior.

This module follows the routing proposed in
[OCA/manufacture issue #1883](https://github.com/OCA/manufacture/issues/1883),
with the transfer creation timing of Odoo's standard three-step flow.
