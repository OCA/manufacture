# Copyright 2025 Binhex - Ariel Brreiros
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Quality Control OCA Test Formula",
    "version": "17.0.1.2.0",
    "category": "Quality Control",
    "license": "AGPL-3",
    "summary": "Auto-compute formulas for Quality Control test questions",
    "author": "Binhex, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["quality_control_oca"],
    "data": [
        "views/qc_test_views.xml",
    ],
    "demo": ["demo/quality_control_demo.xml"],
    "installable": True,
}
