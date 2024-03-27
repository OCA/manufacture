# Copyright 2023 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP Primecontractor Raw Material",
    "summary": "This module helps to handle raw material stock and flow for "
    "subcontracted products.",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion,Odoo Community Association (OCA)",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp_sale_info"],
    "data": [
        "views/mrp_bom_views.xml",
        "views/stock_location_views.xml",
        "views/stock_warehouse_views.xml",
    ],
}
