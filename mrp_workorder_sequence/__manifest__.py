# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "MRP Work Order Sequence",
    "summary": "adds sequence to production work orders.",
    "version": "15.0.1.2.0",
    "category": "Manufacturing",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "development_status": "Beta",
    "maintainers": ["LoisRForgeFlow"],
    "website": "https://github.com/OCA/manufacture",
    "license": "LGPL-3",
    "depends": ["mrp"],
    "data": ["views/mrp_workorder_view.xml"],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
