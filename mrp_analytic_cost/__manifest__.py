# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Manufacturing Materials Analytic Costs",
    "summary": "Track manufacturing costs in real time, using Analytic Items",
    "version": "14.0.1.1.0",
    "category": "Manufacturing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": [
        "mrp_analytic",
        "analytic_activity_based_cost",
        "account_analytic_wip",
    ],
    "data": [
        "views/account_analytic_line_view.xml",
        "views/mrp_production_views.xml",
        "views/mrp_workcenter_view.xml",
    ],
    "maintainer": "dreispt",
    "development_status": "Alpha",
    "installable": True,
}
