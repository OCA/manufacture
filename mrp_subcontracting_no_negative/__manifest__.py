# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "MRP Subcontracting (no negative components)",
    "version": "15.0.0.1.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["sebalix"],
    "summary": "Disallow negative stock levels in subcontractor locations.",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": [
        # core
        "mrp_subcontracting",
    ],
    "data": [],
    "installable": True,
    "auto_install": True,
    "application": False,
}
