# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Work Center Analytic Estimate",
    "summary": "Capture initial estimates and track variances during the \
    manufacturing process",
    "version": "14.0.1.0.1",
    "category": "Manufacturing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": ["mrp_analytic_cost_material"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_workcenter_analytic_estimate.xml",
        "views/mrp_production_view.xml",
    ],
    "installable": True,
    "maintainer": "dreispt",
    "development_status": "Alpha",
}
