# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Quality control - Sign (OCA)",
    "version": "16.0.1.0.1",
    "category": "Quality control",
    "license": "AGPL-3",
    "author": "Kencove, Trobz, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["quality_control_oca", "sign_oca"],
    "data": [
        "security/ir.model.access.csv",
        "views/qc_inspection_view.xml",
        "views/qc_sign_template_item.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [
        "demo/quality_report_demo.xml",
    ],
    "installable": True,
}
