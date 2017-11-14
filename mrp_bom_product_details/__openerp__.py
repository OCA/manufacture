
# -*- coding: utf-8 -*-
# Copyright 2017  Marsal Isern
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Bom product details',
    'summary': """
    This module adds product price and stock to bom view
    """,
    'version': '9.0.1.0.0',
    'author':  "Solutions Libergia inc., "
               "QubiQ, "
               "Odoo Community Association (OCA)",
    'category': 'Manufacturing',
    'depends': ["base", "mrp"],
    'license': 'AGPL-3',
    'data': ['views/mrp_bom_product_details.xml', ],
    'auto_install': False,
    'installable': True,
}
