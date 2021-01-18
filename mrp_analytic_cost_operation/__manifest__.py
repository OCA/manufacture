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
    "depends": ["mrp_analytic", "analytic_activity_based_cost"],
    "data": [
        "views/mrp_workcenter_view.xml",
    ],
    "installable": True,
    "maintainer": "dreispt",
    "development_status": "Alpha",
}
