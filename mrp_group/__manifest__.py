{
    "name": "MRP Group",
    "version": "17.0.0.0.1",
    "category": "Manufacturing",
    "summary": "This module simplifies production management by organizing BOMs and MOs into groups, streamlining complex production processes. It helps identify and group multiple BOMs and MOs involved in producing a finished product, making production management more efficient.",
    "website": "https://github.com/OCA/manufacture",
    "author": "ZestyBeanz Technologies,Odoo Community Association (OCA)",
    "maintainer": "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_bom_view.xml",
        "views/mrp_group_view.xml",
        "views/mrp_production_view.xml",
    ],
    "installable": True,
    "application": False,
}

