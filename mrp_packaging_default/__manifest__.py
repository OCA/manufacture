# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "MRP Default Packaging",
    "summary": "Include packaging info in MRP by default",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Manufacturing/Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["rafaelbn", "yajo"],
    "license": "LGPL-3",
    "depends": ["mrp", "stock_move_packaging_qty"],
    "data": [
        "views/mrp_bom_view.xml",
        "views/mrp_production_view.xml",
    ],
}
