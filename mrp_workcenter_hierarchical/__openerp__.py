# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MRP Workcenter Hierarchical',
    'version': '9.0.1.0.0',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'summary': "Organise Workcenters by section",
    'category': 'Manufacturing',
    'depends': [
        'mrp_operations',
    ],
    'website': 'https://github.com/OCA/manufacture',
    'data': [
        'views/workcenter_view.xml',
    ],
    'demo': [
        'data/mrp_demo.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
