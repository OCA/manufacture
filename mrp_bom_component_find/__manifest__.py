# -*- coding: utf-8 -*-
# Copyright 2018 Tony Galmiche - InfoSaône <tony.galmiche@infosaone.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MRB BOM Component Find (Product Use Case)',
    'version': '10.0.1.0.0',
    'category': 'mrp',
    'summary': 'Know the case of multi-level use of a component from bom',
    'author': 'Tony Galmiche,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/manufacture',
    'license': 'AGPL-3',
    'depends': [
        'mrp',
    ],
    'data': [
        'views/product_views.xml',
        'wizard/mrp_bom_component_find_wizard.xml',
    ],
    'update_xml': [],
    'demo_xml': [],
    'installable': True,
    'application': False,
}
