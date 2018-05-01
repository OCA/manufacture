# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'MRP Production Scheduling',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Schedule Manufacturing Orders based on Work Orders',
    'author': 'Eficent,Odoo Community Association (OCA)',
    'website': 'http://www.eficent.com',
    'license': 'AGPL-3',
    'depends': ['mrp', 'mrp_operations'],
    'data': [
        'view/mrp_view.xml',
    ],
    'test': [],
    "installable": True
}
