Once the BoM operation is configured, the expected duration of every work order
created from that operation is computed as:

```
duration_expected =
    workcenter_start_stop
    + cycle_number × time_cycle         × 100 / efficiency   (standard)
    + time_fixed                        × 100 / efficiency   (fixed setup)
    + cycle_number × capacity / cadence × 100 / efficiency   (cadence)
```

Example — operation with:

- `time_cycle_manual` = 2 min/unit
- `time_fixed` = 10 min (setup)
- `time_cadence` = 5 units/min (= 0.2 min/unit)
- workcenter capacity = 1, efficiency = 100 %
- quantity to produce = 20 units

```
cycle_number          = ceil(qty / capacity) = ceil(20 / 1) = 20
standard contribution = 20 × 2   = 40 min
fixed contribution    =          = 10 min
cadence contribution  = 20 × 0.2 = 4 min
──────────────────────────────────────────
total duration_expected (excl. start/stop) = 54 min
```
