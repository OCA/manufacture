#  Copyright 2022 Simone Rubino - Takobi
#  Copyright 2025 Simone Rubino - PyTech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP production filter lot",
    "summary": "In production order line lots popup, "
    "filter lots based on their location and availability",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture"
    "/tree/14.0/mrp_production_filter_lot",
    "author": "Takobi, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "stock_picking_filter_lot",
    ],
    "auto_install": True,
    "data": [
        "views/stock_picking_type_views.xml",
    ],
}
