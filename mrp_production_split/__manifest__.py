# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MRP Production Split",
    "summary": "Split Manufacturing Orders into smaller ones",
    "version": "14.0.1.0.0",
    "author": "Odoo S.A, Florent THOMAS (M&Go), Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "category": "Manufacturing",
    "external_dependencies": {"python": ["orderedset", ]},
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "templates/messages.xml",
        "views/mrp_production.xml",
        "wizards/mrp_production_split_wizard.xml",
    ],
}
