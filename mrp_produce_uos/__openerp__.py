# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'MRP Produce UOS',
    'version': '8.0.1.0.0',
    'category': 'Manufacturing',
    'author': "Agile Business Group, Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'mrp',
    ],
    'data': [
        'wizard/mrp_product_produce_view.xml',
    ],
    'installable': True,
}
