# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "MRP Production Location Picking Type",
    "summary": "Add production location field to picking types for MRP operations.",
    "version": "15.0.1.0.0",
    "category": "Manufacture",
    "website": "https://github.com/OCA/manufacture",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "depends": ["mrp"],
    "data": [
        "views/stock_picking_type_views.xml",
    ],
    "installable": True,
}
