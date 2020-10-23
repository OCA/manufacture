# -*- coding: utf-8 -*-
# Copyright 2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Manufacturing Orders Auto fill',
    'version': '10.0.1.0.0',
    'category': 'Manufacturing',
    'license': 'AGPL-3',
    'summary': 'Add Auto Fill button in the Produce wizard',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'maintainers': ['alexis-via'],
    'website': 'https://github.com/OCA/manufacture',
    'depends': ['mrp'],
    'data': ['wizard/mrp_product_produce_view.xml'],
    'installable': True,
}
