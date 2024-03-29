# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Quality Control Team OCA",
    "summary": "Adds quality control teams to handle different quality "
    "control workflows",
    "version": "14.0.1.0.0",
    "category": "Quality Control",
    "website": "https://github.com/OCA/manufacture",
    "author": "Eficent, Odoo Community Association (OCA)",
    "maintainers": ["lreficent"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["quality_control_oca"],
    "data": [
        "security/ir.model.access.csv",
        "views/qc_team_view.xml",
        "views/qc_team_dashboard.xml",
        "data/quality_control_team_data.xml",
    ],
}
