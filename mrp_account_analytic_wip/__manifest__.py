# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Manufacturing Accounting for WIP and Variances",
    "summary": "Generate WIP and Variance journal entries for mfg. consumptions",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": ["mrp_account_analytic", "account_analytic_wip"],
    "data": [
        "views/mrp_production_views.xml",
        "views/mrp_workcenter_view.xml",
        "views/mrp_workorder_view.xml",
        "views/stock_location.xml",
    ],
    "demo": ["demo/product_demo.xml"],
    "installable": True,
    "maintainers": ["dreispt"],
    "development_status": "Alpha",
}
