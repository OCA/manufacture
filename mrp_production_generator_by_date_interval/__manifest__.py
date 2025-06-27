# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP Production Generator By Date Interval",
    "version": "17.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/mrp_production_generator_date_interval_wizard_views.xml",
    ],
    "installable": True,
}
