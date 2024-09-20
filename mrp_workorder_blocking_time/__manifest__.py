# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MRP Work Order Blocking Time",
    "category": "Manufacturing",
    "version": "15.0.0.1.0",
    "summary": "Allow to block time on work orders",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_routing_workcenter.xml",
        "views/mrp_workorder.xml",
        "wizards/wizard_open_blocking_popup.xml",
    ],
    "installable": True,
    "maintainers": ["imlopes"],
}
