# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Manufacturing Accounting for WIP and Variances",
    "summary": "Consuming raw materials and operations "
    "generates WIP and Variance journal entries",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": ["account_analytic_wip", "mrp"],
    "data": [
        "views/account_analytic_line_view.xml",
        "views/mrp_production_views.xml",
        "views/mrp_workcenter_view.xml",
    ],
    "installable": True,
    "maintainers": ["dreispt"],
    "development_status": "Alpha",
}
