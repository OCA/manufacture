# Copyright (C) 2023 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "MRP Work Order Cancel",
    "summary": "MRP Workorder Cancel",
    "version": "14.0.1.0.1",
    "category": "Manufacturing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "development_status": "Beta",
    "maintainers": ["Hardik-OSI"],
    "website": "https://github.com/OCA/manufacture",
    "license": "LGPL-3",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_workorder_view.xml",
        "wizard/work_order_cancel_wiz_view.xml",
    ],
    "installable": True,
}
