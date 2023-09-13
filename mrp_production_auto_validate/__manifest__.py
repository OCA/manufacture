# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Manufacturing Order Auto-Validate",
    "summary": "Manufacturing Order Auto-Validation when components are picked",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/manufacture",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [
        "views/mrp_bom.xml",
        "views/mrp_production.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["sebalix"],
}
