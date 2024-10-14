# Copyright 2024 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Quality Control - Timesheet (OCA)",
    "version": "17.0.1.0.0",
    "category": "Quality Control",
    "website": "https://github.com/OCA/manufacture",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["quality_control_oca", "hr_timesheet"],
    "data": ["views/qc_inspection_view.xml"],
}
