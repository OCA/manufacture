# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) All Rights Reserved 2015 Akretion
#    @author David BEAL <david.beal@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


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
        'workcenter_view.xml',
        'transient/mrp_view.xml',
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
