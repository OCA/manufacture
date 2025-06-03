# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MRP Workorder Reference",
    "summary": "Set Internal References to BoM Operations and Work Orders",
    "version": "15.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [
        "views/mrp_routing_workcenter.xml",
        "views/mrp_workorder.xml",
    ],
}
