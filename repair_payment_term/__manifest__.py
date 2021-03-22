# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Repair Payment Term',
    'summary': """
        This module add to Repair Orders the *Payment Term* field""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/manufacture',
    'maintainers': ['mileo'],
    'depends': [
        'repair',
    ],
    'data': [
        'views/repair_order.xml',
        'report/repair_report_templates.xml',
    ],
    'demo': [
    ],
}
