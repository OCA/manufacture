# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Andrea Gallina
#    Copyright 2015 Apulia Software srl
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
