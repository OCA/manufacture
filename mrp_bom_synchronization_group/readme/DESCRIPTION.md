This module introduces the concept of a **BoM Synchronization Group**: a set of
Bills of Materials that must share the same consumed components.

The Bills of Materials of a group do not need to produce the same finished
product. Only their components are kept aligned (product, quantity, unit of
measure and variant applicability); operations and routings are intentionally
ignored, so the same components can be produced through different work centers
while staying consistent.

The module:

- adds a **BoM Synchronization Group** model with its own menu, where existing
  Bills of Materials are linked (a Bill of Materials can belong to a single
  group);
- detects component discrepancies between the members and flags them on the
  group and on each member Bill of Materials;
- can either warn and let the user fix the discrepancies manually, or keep the
  members synchronized automatically;
- only touches components: operations are preserved, and a hook lets dependent
  modules resolve the operation of synchronized lines.