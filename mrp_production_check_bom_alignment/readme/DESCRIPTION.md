This module checks that a Manufacturing Order's components, by-products, and
operations are consistent with its current Bill of Materials.

Seven alignment checks are performed:

- **Components** — the set of BoM lines linked to the MO's raw moves matches
  the BoM exactly (no added or removed lines).
- **Operations** — the set of operations in the MO's work orders matches the
  BoM's operation list exactly.
- **Component quantities** — each raw move's demand quantity matches the
  BoM line quantity scaled to the MO production quantity.
- **Consumed in Operation** — each raw move's operation (recorded on the move
  when the MO was created) matches the current "Consumed in Operation" defined
  on its BoM line.
- **By-products** — the set of BoM by-products linked to the MO's finished
  moves matches the BoM exactly (no added or removed by-products).
- **By-product quantities** — each by-product move's demand quantity matches
  the BoM by-product quantity scaled to the MO production quantity.
- **Produced in Operation** — each by-product move's operation matches the
  current "Produced in Operation" defined on its BoM by-product.

When a misalignment is detected:

- A **warning banner** is shown at the top of the Manufacturing Order form
  for any MO that is not yet done or cancelled.
- When **confirming** a misaligned MO, a dialog is shown giving the user the
  choice to fix it, go back or confirm it anyway.
