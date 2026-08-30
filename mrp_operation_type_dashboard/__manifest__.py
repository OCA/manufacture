# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP Operation Type Dashboard",
    "summary": "Adds a kanban overview of manufacturing operation types to "
    "the Manufacturing app",
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["mrp", "stock"],
    "data": [
        "views/stock_picking_type_views.xml",
    ],
}
