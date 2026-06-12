# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "MRP BOM Assign Auto",
    "version": "18.0.1.0.0",
    "category": "Manufacturing",
    "summary": "Auto select th first BoM that has all components available",
    "website": "https://github.com/OCA/manufacture",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["mrp"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
}
