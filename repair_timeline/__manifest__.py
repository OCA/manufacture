# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Repair Timeline',
    'summary': """
        Add timeline view""",
    'category': 'Manufacturing',
    'version': '12.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'maintainers': ['marcelsavegnago'],
    'website': 'https://github.com/oca/manufacture',
    'images': ['static/description/banner.png'],
    'depends': [
        'base_repair',
        'web_timeline'
    ],
    'data': [
        'views/repair_order.xml'
    ],
}
