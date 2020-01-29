# -*- coding: utf-8 -*-
#  Copyright 2019 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Quality control formula",
    "summary": "Use formulas in inspection lines.",
    "version": "10.0.1.0.0",
    "development_status": "Beta",
    "category": "Quality control",
    "website": "https://github.com/OCA/manufacture/tree/"
               "10.0/quality_control_formula",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "quality_control",
    ],
    "data": [
        "views/qc_inspection_line_views.xml",
        "views/qc_inspection_views.xml",
        "views/qc_test_question_views.xml",
        "views/qc_test_views.xml"
    ]
}
