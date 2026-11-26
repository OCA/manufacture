To configure the default synchronization behaviour:

1. Go to *Manufacturing > Configuration > Settings*.
2. Under *Operations*, set **BoM Synchronization Group** to either:
   - *Warning and fix manually*: discrepancies between the members of a group
     are flagged and a wizard lets you align the components on demand.
   - *Synchronize automatically*: changing the components of any Bill of
     Materials in a group propagates the change to the other members.

This default is assigned to every new group on creation. Each group can then
change its own **Synchronization Mode** field independently.