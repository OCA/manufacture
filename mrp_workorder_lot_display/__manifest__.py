# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "MRP Workorder Lot Display",
    "summary": "Display lot number on workorders kanban",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["grindtildeath"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp",
    ],
    "data": [
        "views/mrp_workorder.xml",
    ],
}
