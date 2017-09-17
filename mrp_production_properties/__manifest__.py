# -*- coding: utf-8 -*-
# Copyright 2014 <alex.comba@agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Mrp Production Properties",
    'version': '10.0.1.0.0',
    'category': 'Manufacturing',
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'sale_mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_view.xml',
    ],
    'installable': True,
}
