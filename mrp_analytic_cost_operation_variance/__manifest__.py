# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Manufacturing Operations Estimate and Variances",
    "summary": "Capture operation initial estimates and track variances \
    during the manufacturing process",
    "version": "14.0.1.0.1",
    "category": "Manufacturing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": ["mrp_analytic_cost_variance", "mrp_analytic_cost_operation"],
    "data": [
        "views/mrp_workcenter_analytic_estimate_view.xml",
        "views/mrp_workorder_view.xml",
    ],
    "installable": True,
}
