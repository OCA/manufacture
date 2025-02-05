# Copyright 2025 Edilio Escalona Almira - Binhexteam
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Quality Control Attachment OCA",
    "version": "16.0.1.0.0",
    "category": "Quality Control",
    "license": "AGPL-3",
    "summary": "This module allows you to add attachments to quality control inspections.",
    "author": "Binhexteam, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["quality_control_oca"],
    "data": [
        """views/qc_inspection_views.xml""",
        """views/qc_test_views.xml""",
    ],
    "installable": True,
}
