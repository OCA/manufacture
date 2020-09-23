# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Production Show Post Inventory',
    'version': '12.0.1.0.1',
    'category': 'MRP',
    'author': 'Camptocamp, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/manufacture',
    'license': 'AGPL-3',
    'depends': [
        'mrp',
    ],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True,
}
