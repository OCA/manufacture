Only one component line can have a propagation profile per BoM, and the
component must be tracked by lots or serial numbers.

Propagated fields are grouped in profiles. To create one:

1. Go to **Manufacturing > Configuration > Lot Info Propagation Profiles**.
2. Create a profile.
3. Select the stock lot fields that the profile should propagate.

To configure product category defaults:

1. Go to a product category.
2. Set **MRP Lot Propagation Profile**.

That profile will be proposed automatically on BoM lines when selecting a
component from that category.

To configure a BoM:

1. Open the BoM.
2. On the component line that should provide the lot information, review or edit
   the lot propagation profile.
3. Leave the profile empty on the other component lines.
4. On by-product lines that should receive the same lot information, enable
   **Propagate Lot Info**.

For manufacturing orders created without a BoM, configure the propagation profile
on the manufactured product category. The order must consume exactly one
lot/serial number across all raw material moves.
