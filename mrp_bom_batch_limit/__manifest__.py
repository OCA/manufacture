# Copyright 2025 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP BoM Batch Limit",
    "summary": "Set min/max quantity limits for production orders with validation",
    "version": "17.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/mrp_bom_views.xml",
        "views/mrp_production_views.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
