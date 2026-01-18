# Copyright 2025 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP - BoM Batch Size backport from 19.0",
    "summary": "Configure batch sizes for automatic manufacturing orders",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Odoo SA, Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/mrp_bom_views.xml",
        "wizard/mrp_production_split.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    "development_status": "Beta",
}
