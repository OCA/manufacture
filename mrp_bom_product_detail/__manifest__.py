# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Bom product details',
    'version': '10.0.1.0.0',
    'author': "Solutions Libergia inc.,Odoo Community Association (OCA)",
    'license': 'GPL-3 or any later version',
    'category': 'Manufacturing',
    'depends': [
        "mrp",
    ],
    'data': [
        'views/mrp_bom_product_details.xml',
    ],
    'auto_install': False,
    'installable': True,
}
