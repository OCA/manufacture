# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin Dupont (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Product Characterisation",
    "summary": "Adds product characterisation 'Intermediate Products'.",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "author": "GRAP, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/view_mrp_bom.xml",
        "views/view_product_product.xml",
        "views/view_product_template.xml",
    ],
    "installable": True,
}
