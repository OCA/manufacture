# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "MRP Default Workorder Time",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "license": "LGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["ChrisOForgeFlow"],
    "summary": "Adds an MRP default workorder time",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp", "stock"],
    "data": [
        "views/res_config_settings_view.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
}
