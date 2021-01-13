# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Manufacturing Materials Analytic Costs",
    "summary": "Track raw material costs as Analytic Items during the \
    manufacturing process",
    "version": "14.0.1.0.1",
    "category": "Manufacturing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": ["mrp_analytic"],
    "data": ["views/account_analytic_line_view.xml", "views/mrp_production_views.xml"],
    "maintainer": "dreispt",
    "development_status": "Alpha",
    "installable": True,
}
