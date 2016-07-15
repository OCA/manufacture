# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MRP Load',
    'version': '0.3',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'summary': "Workcenters load computing",
    'category': 'Manufacturing',
    'depends': [
        'mrp_workcenter_hierarchical',
        'mrp_workcenter_workorder_link',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
        'views/workcenter_view.xml',
        'wizard/switch_workcenter.xml',
    ],
    'demo': [
        'demo/mrp_demo.xml'
    ],
    'external_dependencies': {
        'python': [],
    },
    'license': 'AGPL-3',
    'tests': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
