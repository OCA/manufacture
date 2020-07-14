# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Manufacturing Order Type",
    "version": "13.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "website": "https://github.com/OCA/manufacture",
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/manufacturing_order_type_views.xml",
        "views/mrp_production_views.xml",
        "views/product_views.xml",
        "data/manufacturing_order_type.xml",
    ],
    "installable": True,
    "auto_install": False,
}
