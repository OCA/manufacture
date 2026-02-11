{
    "name": "Quality Control OCA Inspection Matrix",
    "summary": "Quality inspection tests with 2D matrix view.",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Quality Control",
    "website": "https://github.com/OCA/manufacture",
    "author": "Le Filament, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "quality_control_oca",
        "web_widget_x2many_2d_matrix",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/multi_quality_edit_wizard_view.xml",
    ],
}
