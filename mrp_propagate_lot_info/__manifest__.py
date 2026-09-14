# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
{
    "name": "MRP Propagate Lot Info",
    "summary": "Propagate lot data from the origin consuming materials",
    "version": "18.0.1.0.0",
    "author": "Moduon, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Warehouse",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_lot_info_propagation_profile.xml",
        "views/mrp_bom.xml",
        "views/mrp_production.xml",
        "views/product_category.xml",
    ],
    "demo": ["demo/mrp_propagate_lot_info_demo.xml"],
    "license": "LGPL-3",
    "maintainers": ["chienandalu"],
}
