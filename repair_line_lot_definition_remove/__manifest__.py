# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Repair Line Lot Definition Remove',
    'summary': """
        Remove Need Lot/Serial Parts Definition""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/manufacture',
    'images': ['static/description/banner.png'],
    'category': 'Repair',
    'maintainers': ['marcelsavegnago'],
    'depends': [
        'repair_stock_move',
    ],
    'data': [
        'views/repair_order.xml',
    ],
}
