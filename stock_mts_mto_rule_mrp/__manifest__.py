# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock MTS+MTO Rule for manufacturing',
    'summary': 'Add support for MTS+MTO route on manufacturing',
    'version': '12.0.1.0.0',
    'development_status': 'Alpha',
    'category': 'Warehouse',
    'website': 'https://github.com/OCA/manufacture',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'stock_mts_mto_rule',
        'mrp'
    ],
    'auto_install': True,
}
