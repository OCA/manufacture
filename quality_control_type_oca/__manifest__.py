# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Quality Control Type OCA",
    "version": "18.0.1.0.0",
    "category": "Quality Control",
    "license": "AGPL-3",
    "summary": "Add type Quality Control",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["quality_control_oca"],
    "data": [
        "data/quality_control_data.xml",
        "security/ir.model.access.csv",
        "views/qc_inspection_view.xml",
        "views/qc_inspection_type_view.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
}
