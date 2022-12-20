# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "MRP Production Inject Operation",
    "summary": "Adds an existing operation from the Bill of Material",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["grindtildeath"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp_workorder_sequence",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production.xml",
        "views/mrp_workorder.xml",
        "wizard/mrp_workorder_injector.xml",
    ],
}
