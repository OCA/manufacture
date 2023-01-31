# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MRP Workcenter Category",
    "summary": "Adds a category to workcenters",
    "version": "15.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_workcenter_category.xml",
        "views/mrp_workcenter.xml",
    ],
    "demo": ["demo/mrp_workcenter_category.xml"],
}
