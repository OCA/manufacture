# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "MRP Production Push MTO Quantity",
    "summary": "Push the quantity produced by a manufacturing order "
    "to the demand of the ensuing MTO moves",
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mrp"],
    "data": ["views/stock_picking_type_views.xml"],
}
