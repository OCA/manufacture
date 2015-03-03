# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
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
##############################################################################

{
    'name': 'Procurement Improvement - supply method',
    'version': '1.0',
    'author': 'Elico Corp',
    'website': 'www.openerp.net.cn',
    'category': 'Generic Modules/Production',
    'depends': ['procurement', 'sale', 'mrp', 'purchase'],
    'description': """
This module aims to add more flexibility on procurement management.
    - Allowing planner changing the supply method on the procurement order level by
        adding a new field supply_method for planner to confirm.
    - Allowing planner changing the procurement method and supply method
        before the procurement order is running.
======
Note:
======
This module redefine the field: procure_method which is defined in moudle: procurement
    """,
    'data': [
        'procurement_supply_method_views.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
