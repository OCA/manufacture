# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Quality Control Team",
    "summary": "Adds quality control teams to handle different quality "
    "control workflows",
    "version": "13.0.1.0.0",
    "development_status": "Mature",
    "category": "Quality Control",
    "website": "https://github.com/OCA/manufacture",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["lreficent"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["quality_control"],
    "data": [
        "security/ir.model.access.csv",
        "views/qc_team_view.xml",
        "views/qc_team_dashboard.xml",
        "data/quality_control_team_data.xml",
    ],
}
