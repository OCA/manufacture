Extends BOM Operations (`mrp.routing.workcenter`) with two additional fields
for advanced work order duration calculation:

- **Fixed Duration** (`time_fixed`): flat minutes added to every work order for
  the operation, independent of the quantity to produce.
- **Cadence** (`time_cadence`): production rate expressed in units per minute.
  The module derives `qty / cadence` minutes of working time from this value.

Both contributions are added on top of the standard *minutes-per-unit*
(`time_cycle_manual`) and are subject to the workcenter efficiency factor.
