# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Unbuild orders with return subcontracting",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "category": "Manufacture",
    "summary": "Unbuild orders are created automatically "
    "when is returned a product subcontracted",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp_account", "mrp_subcontracting"],
    "data": ["views/mrp_unbuild_views.xml"],
    "installable": True,
}
