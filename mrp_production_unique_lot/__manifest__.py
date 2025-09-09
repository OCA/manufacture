# Copyright 2025 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "MRP Production Unique Lot",
    "Summary": "Ensures that production lot numbers are unique and cannot be reused "
    "in another manufacturing order.",
    "version": "16.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/stock_picking_views.xml",
        "views/mrp_production_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
