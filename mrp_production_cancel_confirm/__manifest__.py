# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Production Cancel Confirm",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "category": "Usability",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["base_cancel_confirm", "mrp"],
    "data": [
        "views/mrp_production_views.xml",
    ],
    "auto_install": False,
    "installable": True,
}
