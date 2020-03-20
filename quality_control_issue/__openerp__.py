# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Quality Control Issue",
    "summary": "Allow to manage and report Quality Control Issues.",
    "version": "9.0.1.0.0",
    "category": "Quality Control",
    "website": "https://odoo-community.org/",
    "author": "Eficent , Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["quality_control", "quality_control_team", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "security/quality_control_issue_security.xml",
        "data/qc_issue_sequence.xml",
        "data/qc_stage_data.xml",
        "views/qc_issue_view.xml",
        "views/qc_problem_view.xml",
        "views/qc_problem_group_view.xml",
        "views/qc_team_dashboard_view.xml",
    ],
}
