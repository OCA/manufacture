After installing the module, review the subcontracting warehouse and supplier
configuration before creating operational documents.

## Warehouse configuration

On each warehouse that will manage subcontracted work orders, set the
subcontracting operation types:

- **Subcontract Picking Type OUT**:
  use **Subcontracting OUT (Parts)**.
- **Subcontract Picking Type IN**:
  use **Subcontracting IN (Parts)**.
- **Subcontract Virtual Picking Type OUT**:
  use **Subcontracting OUT (Finished)**.
- **Subcontract Virtual Picking Type IN**:
  use **Subcontracting IN (Finished)**.

The module creates the default subcontracting operation types and two purchase
order types:

- **Subcontracting**
- **Subcontracting - Instant return**

The purchase order types are configured with the subcontracting operation types
and allow managing the standard purchase flow and the immediate-return variant.

## Operation type locations

Check that the subcontracting operation types use the expected source and
destination locations:

- **Subcontracting OUT (Parts)**

  - Source: **WH/Stock** (or **WH/Giacenza**, depending on the database
    language).
  - Destination: **Subcontractors/General Stock**.

- **Subcontracting IN (Parts)**

  - Source: **Virtual Locations/Production/General Stock**.
  - Destination: **Virtual Locations/Production**.

- **Subcontracting OUT (Finished)**

  - Source: **Virtual Locations/Production**.
  - Destination: **Virtual Locations/Production/Finished Subcontract**.

- **Subcontracting IN (Finished)**

  - Source: **Virtual Locations/Production/Finished Subcontract**.
  - Destination: **Virtual Locations/Production**.

## Supplier-specific locations

The default locations are templates for supplier-specific locations:

- Duplicate **Subcontractors/General Stock** to create the real parts location
  for each subcontractor.
- Duplicate **Virtual Locations/Production/Finished Subcontract** to create the
  virtual finished-product location for each subcontractor.

Creating one pair of locations per subcontractor is recommended. Without
supplier-specific locations, the stock flow still works, but it is not possible
to track the real quantity of parts and finished goods at each subcontractor.

After creating the supplier-specific locations, open the supplier contact and
set:

- **Subcontract Location**:
  the real parts location for that subcontractor.
- **Subcontract Virtual Location**:
  the virtual location used for finished products for that subcontractor.

## Bill of materials and work order configuration

For each BoM operation, you can optionally enable subcontracting and define:

- whether the operation can be subcontracted;
- the allowed subcontractors;
- the service product to put on the purchase order line.

This configuration is optional on the BoM operation. It can also be enabled or
changed directly on the work order.

When subcontracting is configured on the BoM operation, the values are copied to
the generated work order. They can still be changed on the work order until
subcontracting documents are created.
