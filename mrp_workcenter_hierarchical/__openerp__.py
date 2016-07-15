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
    'website': 'http://www.akretion.com/',
    'data': [
        'views/workcenter_view.xml',
    ],
    'demo': [
        'demo/mrp_demo.xml',
    ],
    'license': 'AGPL-3',
    'tests': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
