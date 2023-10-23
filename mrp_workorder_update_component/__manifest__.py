# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "MRP Work Order Update Component",
    "summary": "Allows to modify component lines in work orders.",
    "version": "13.0.1.0.0",
    "category": "Manufacturing",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["DavidJForgeFlow"],
    "website": "https://github.com/OCA/manufacture",
    "license": "LGPL-3",
    "depends": ["mrp"],
    "data": [
        "views/mrp_workorder_view.xml",
        "wizards/mrp_workorder_new_line_view.xml",
    ],
    "installable": True,
}
