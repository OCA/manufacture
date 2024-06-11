# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "MRP Set Quantity To Reservation",
    "version": "15.0.0.1.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": [
        "CarlosRoca13",
        "sergio-teruel",
    ],
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": [
        "mrp",
    ],
    "data": ["views/mrp_production_views.xml"],
    "installable": True,
    "auto_install": True,
    "application": False,
}
