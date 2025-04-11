# Copyright 2025 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP Workorder Last Worker",
    "summary": "See the last user who worked on a workorder",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp"],
    "data": [
        "views/mrp_workorder_views.xml",
    ],
    "application": False,
    "installable": True,
}
