# Copyright 2023 Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "MRP Partial Consumption",
    "summary": "Allows to consume partial quantities in manufacturing orders",
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "maintainers": ["alan196"],
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Jarsa,Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mrp"],
    "data": [
        "views/mrp_production_view.xml",
        "security/res_groups.xml",
    ],
}
