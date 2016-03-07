# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Product version',
    'version': '8.0.0.0.0',
    'category': 'Manufacturing',
    'summary': "",
    'author': 'Sergio Corato - SimplERP Srl',
    'website': 'http://simplerp.it',
    'depends': [
        'mrp',
        'product_sequence',
    ],
    'data': [
        'security/product_version_security.xml',
        'views/res_config_view.xml',
        'views/product_view.xml',
    ],
    'installable': True,
    "post_init_hook": "set_active_product_active_state",
}
