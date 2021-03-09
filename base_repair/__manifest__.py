# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Repair",
    "summary": """
        This module extends the functionality of Odoo Repair module
        to add some basic features.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo, Agile Business Group, Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "images": ["static/description/banner.png"],
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["repair"],
    "data": ["views/repair_order.xml"],
    "installable": True,
}
