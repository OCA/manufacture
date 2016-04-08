# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "BOM Dismantling",
    "summary": "Ability to create a dismantling BOM by reversing a BOM.",
    "version": "9.0.1.0.0",
    "category": "Manufacturing",
    "website": "http://www.camptocamp.com/",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'mrp_byproduct',
        "stock_available_mrp",
    ],
    "data": [
        "views/mrp_bom.xml",
        "views/product_template.xml",
        "wizards/mrp_product_produce.xml",
    ],
}
