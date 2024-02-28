# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Quentin Dupont (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP BoM Simple Report",
    "summary": "Print simple report for your Bill of Materials",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "author": "GRAP, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": [
        "mrp",
    ],
    "assets": {
        "web.report_assets_common": [
            "/mrp_bom_simple_report/static/src/scss/mrp_bom_simple_report.scss"
        ],
    },
    "data": [
        "data/report_paperformat.xml",
        "report/report_simple_bom.xml",
        "report/ir_actions_report.xml",
    ],
    "installable": True,
}
