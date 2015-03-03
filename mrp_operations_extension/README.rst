MRP operations extension module
===============================

This module adds:

- New table to store operations to avoid typing them again.
- Adds a relation from WorkcenterLines to BoM Lists.
- Adds a relation from WorkcenterLines to Manufacturing Orders in Scheduled/Consumed/Finished Products.
- Adds a relation between Routing Work Center Lines and Work Center extra Info.

Controls the availability of material in operations, and controls operation
start with respect to previous.
