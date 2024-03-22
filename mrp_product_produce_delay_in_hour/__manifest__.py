# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin Dupont (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Product Produce Delay in Hour",
    "summary": "Handle MRP Product Produce Delay in hours not in days.",
    "version": "16.0.1.0.0",
    "author": "GRAP, Odoo Community Association (OCA)",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "maintainers": ["quentinDupont"],
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "data": [
        "views/product_template.xml",
        "data/decimal_precision.xml",
    ],
    "installable": True,
}
