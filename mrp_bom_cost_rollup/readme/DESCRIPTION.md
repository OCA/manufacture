This module rolls up the cost of a Bill of Materials and lets you write
the result onto the manufactured product's cost (`standard_price`).

For each BoM it computes:

- **BoM Cost** – the cost to produce one *batch* (the BoM quantity) of
  the product: the sum of every component cost, **recursively through
  sub-BoMs**, plus operation costs (manual operation time × work center
  hourly cost).
- **BoM Unit Cost** – the BoM Cost divided by the BoM quantity, i.e. the
  rolled-up cost of a single produced unit.

Community Odoo can display a BoM cost in the *BoM Overview* report, but
it has no way to *persist* that rolled-up cost as the product's standard
cost. This module fills that gap with a one-click action on the BoM and
on the product.
