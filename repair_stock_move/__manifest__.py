# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

{
    "name": "Repair Stock Move",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "category": "RMA",
    "summary": "Ongoing Repair Stock Moves Definition in odoo",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["repair"],
    "data": [
        "views/repair_order_views.xml",
    ],
    "post_load": "post_load_hook",
    "installable": True,
    "application": False,
}
