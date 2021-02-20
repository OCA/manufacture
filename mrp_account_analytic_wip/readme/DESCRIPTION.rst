Out of the box, manufacturing costs are only generated
when a Manufacturing Order is closed.

There are cases where the manufacturing costs need to be tracked in real time.
This is especially important for manufacturing scenarios with a long cycle time,
spanning significant period of time.

This feature allows to track costs while the manufacturing is in progress,
both for raw materials used and work order operations.

When operations are consumed in a Manufacturing Order, Analytic Items are generated for
the corresponding costs.
Costs incurred are stored as Analytic Items, and can then be analyzed.
No journal entries are immediately generated.

A scheduled job uses the Analytic Item data to generate journal entries for manufacturing
WIP and variances versus the quantities/amounts expected to be consumed.
