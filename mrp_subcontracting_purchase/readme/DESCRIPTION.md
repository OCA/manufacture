This bridge module adds some smart buttons between Purchase and Subcontracting

**DISCLAIMER:** This module is a backport from Odoo SA and as such, it is not included
in the OCA CLA.

That means we do not have a copy of the copyright on it like all other OCA modules.

This is a backporting of features from mrp_subcontracting modules from v15 allowing to
setup a flow addressing the following use case:

Vendor 1 manufactures and sells “Finished Product”

Vendor 2 manufactures and sells “Component Product” (used to manufacture “Finished
Product”)

Vendor 3 sells “Element Product” (used to manufacture “Component Product”)

As an example, in the case where there is no available qty for each of these three
products, creating a PO purchasing “Finished product” for Vendor 1 generates:

- The standard receipt picking from Vendor 1 to our warehouse
- A PO for Vendor 2 for product “Component Product”
- A subcontracting order for Vendor 1 for “Finished Product”, with component location:
  Vendor 1 subcontracting location

Once this PO is confirmed, this generates:

- A dropship picking for Vendor 1 from Vendor 2 for “Component Product”
- A subcontracting order for Vendor 2 for “Component Product”, with component location:
  Vendor 2 subcontracting location
- A PO for Vendor 3 for product “Element Product”

Once this PO is confirmed, this generates:

- A dropship picking for Vendor 2 from Vendor 3 for “Element Product”
