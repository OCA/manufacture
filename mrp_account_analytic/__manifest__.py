# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Manufacturing Analytic Items",
    "summary": "Consuming raw materials and operations generated Analytic Items",
    "version": "14.0.1.0.1",
    "category": "Manufacturing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": ["mrp_analytic"],
    "data": [
        "views/account_analytic_line_view.xml",
    ],
    "installable": True,
    "maintainers": ["dreispt"],
    "development_status": "Beta",
}
