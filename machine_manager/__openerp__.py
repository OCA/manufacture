
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    'name': 'Machine Manager',
    'version': '1.0',
    'description': """This module is a vertical for Machinery management.""",
    'author': 'OdooMRP team',
    'website': 'http://www.odoomrp.com',
    "depends": ['stock', 'account'],
    "category": "Generic Modules",
    "data": ['views/machinery_view.xml',
             'views/machine_model_view.xml',
             'views/machinery_users_view.xml',
             'views/product_view.xml',
             'security/machinery_security.xml',
             'security/ir.model.access.csv',
             ],
    "installable": True
}
