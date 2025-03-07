# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP Stock Move Actual Date",
    "version": "16.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "MRP",
    "license": "AGPL-3",
    "depends": ["mrp", "stock_move_actual_date"],
    "data": [
        "views/mrp_production_views.xml",
        "views/mrp_unbuild_views.xml",
    ],
    "installable": True,
}
