# Copyright (C) 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

{
    "name": "Repair Reinvoice",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "license": "LGPL-3",
    "category": "Repair",
    "summary": "Repair Reinvoice in odoo",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["repair"],
    "data": ["views/repair_views.xml"],
    "maintainer": "mariadforgeflow",
    "installable": True,
    "application": False,
    "post_init_hook": "post_init_hook",
}
