# -*- coding: utf-8 -*-
#
# Author: Andrea Gallina
# ©  2015 Apulia Software srl
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Mrp Production Hierarchy',
    'version': '8.0.1.0.0',
    'category': 'mrp',
    'author': 'Apulia Software srl, Odoo Community Association (OCA)',
    'maintainer': 'Odoo Community Association (OCA)',
    'website': 'www.apuliasoftware.it',
    'license': 'AGPL-3',
    'depends': [
        'mrp'
    ],
    'data': [
        'views/mrp_production_view.xml',
        'wizard/wizard_hierarchy_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
