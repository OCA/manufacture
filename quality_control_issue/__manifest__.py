# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Aleph Objects, Inc. (https://www.alephobjects.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Quality Control Issue",
    "summary": "Allow to manage and report Quality Control Issues.",
    "version": "11.0.1.1.0",
    "development_status": "Production/Stable",
    "category": "Quality Control",
    "website": "https://odoo-community.org/",
    "author": "Eficent , Odoo Community Association (OCA)",
    "maintainers": ["lreficent"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "quality_control",
        "quality_control_team",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/quality_control_issue_security.xml",
        "data/qc_issue_sequence.xml",
        "data/qc_stage_data.xml",
        "views/qc_issue_view.xml",
        "views/qc_problem_view.xml",
        "views/qc_problem_group_view.xml",
        "views/qc_team_dashboard_view.xml",
        "views/stock_scrap_view.xml",
        "views/qc_issue_stage.xml",
        "views/qc_problem_stage.xml",
    ],
}
