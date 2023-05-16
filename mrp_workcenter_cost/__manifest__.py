# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Manufacturing - Workcenter Cost Duration",
    "summary": "Controls how to compute the workcenter cost (effective vs theoretical)",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Manufacturing/Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "depends": [
        "mrp_account",
    ],
    "data": [
        "views/product_template.xml",
    ],
    "installable": True,
    "auto_install": False,
    "development_status": "Beta",
    "maintainers": ["ivantodorovich", "sebalix"],
}
