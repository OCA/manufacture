# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "MRP Serial Number Propagation",
    "version": "18.0.1.1.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["sebalix"],
    "summary": "Propagate a serial number from a component to a finished product",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_bom.xml",
        "views/mrp_production.xml",
        "wizard/mrp_batch_produce_propagate.xml",
        "wizard/mrp_batch_produce.xml",
    ],
    "installable": True,
    "application": False,
}
