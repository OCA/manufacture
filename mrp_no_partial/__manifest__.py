# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mrp No Partial',
    'summary': """
        Block the production order if all quantities are not done""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/manufacture',
    'depends': [
        'mrp',
    ],
    'data': [
        'views/stock_picking_type.xml',
    ],
}
