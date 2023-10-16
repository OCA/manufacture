- Enable Multi-step Routes in Inventory > settings
- Unarchive operation type “Subcontracting”

For each subcontracting partner:

- Create a subcontracting location with parent location “Physical
  Locations/Subcontracting Location”
- Set created location in subcontracting partner > tab Sales & Purchase >
  “Subcontracting location” field
- Create two rules for Route “Dropship Subcontractor on Order:
  - Action: Buy, Operation Type: Dropship, Destination location: partner subcontracting
    location
  - Action: Pull From, Operation Type: Subcontracting, Source Location: partner
    subcontracting location, Destination location: Virtual Locations/Production, Supply
    Method: Trigger Another Rule, Partner Address: subcontracting partner

For each product:

- Create a Vendor Pricelist and a Subcontracting BoM.
- In Inventory tab, set Route “Buy” for Finished Product, and “Dropship Subcontractor on
  order” for products needed for its production.
