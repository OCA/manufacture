To group Bills of Materials:

1. Go to *Manufacturing > Products > BoM Synchronization Groups*.
2. Create a group, give it a name and add the Bills of Materials that must
   share the same components. Only Bills of Materials not yet assigned to a
   group can be selected.

The behaviour when the members diverge depends on the group's
**Synchronization Mode** (its default is set in *Settings*, see Configuration):

- **Warning and fix manually**: a warning is shown on the group and on each
  member Bill of Materials. Use the **Synchronize Components** button on the
  group to pick a reference Bill of Materials, preview the planned changes per
  Bill of Materials and apply them. Members cannot be synchronized from the
  Bill of Materials form itself.
- **Synchronize automatically**: editing the components of any member
  immediately propagates the change to the other members of the group.

In both cases only components are synchronized: existing component lines keep
their operation assignment, and only added, removed or modified components are
touched.