# Copyright 2018 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Production Grouped By Product',
    'version': '11.0.1.0.0',
    'category': 'MRP',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/manufacture',
    'license': 'AGPL-3',
    'depends': [
        'mrp',
    ],
    'data': [
        'views/stock_picking_type_views.xml',
    ],
    'installable': True,
}
