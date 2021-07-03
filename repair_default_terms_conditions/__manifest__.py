# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Repair Default Terms Conditions',
    'summary': """
        This module allows repair default terms & conditions""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/manufacture',
    'category': 'Manufacturing',
    'maintainers': ['marcelsavegnago'],
    'images': ['static/description/banner.png'],
    'depends': [
        'base_repair_config',
    ],
    'data': [
        'views/res_config_settings.xml',
    ],
}
