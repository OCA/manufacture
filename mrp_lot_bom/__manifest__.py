# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "MRP Lot BoM",
    "version": "17.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "summary": "Shows on lots/serial numbers and on the inventory the "
    "Bill of Materials they were manufactured with",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [
        "views/stock_lot_views.xml",
        "views/stock_quant_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "license": "LGPL-3",
    "installable": True,
}
