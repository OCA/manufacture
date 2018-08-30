# Copyright 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP MTO with Stock Purchase",
    "summary": "Module needed to make mrp_mto_with_stock module compatible "
               "with purchase module.",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp_mto_with_stock",
        "purchase"
    ],
    "auto_install": True,
}
