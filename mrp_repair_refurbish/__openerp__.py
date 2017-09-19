# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "MRP Repair Refurbish",
    "summary": "Create refurbished products during repair",
    "version": "9.0.1.0.1",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'mrp_repair',
    ],
    "data": [
        "views/mrp_repair_view.xml",
        "data/stock_data.xml",
        "views/product_template_view.xml",
        "views/product_product_view.xml",
    ],
}
