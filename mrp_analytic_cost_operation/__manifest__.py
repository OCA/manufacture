# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Manufacturing Operations Analytic Costs",
    "summary": "Track work center operation costs as Analytic Items during \
    the manufacturing process",
    "version": "14.0.1.0.1",
    "category": "Manufacturing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": ["mrp_analytic_cost_material"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_workcenter_view.xml",
        "views/account_analytic_line_view.xml",
    ],
    "installable": True,
}
