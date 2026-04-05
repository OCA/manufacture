# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Printing Auto MRP",
    "version": "18.0.1.0.1",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "data": [
        "security/ir_rule.xml",
        "views/mrp_production.xml",
        "views/stock_picking_type.xml",
    ],
    "depends": [
        "printing_auto_stock_picking",
        "mrp",
    ],
    "license": "AGPL-3",
}
