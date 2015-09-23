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
    'name': "mrp_mto_with_stock",

    'summary': """
        Fix Manufacturing orders to pull from stock until qty is zero,
        and then create a procurement for them""",

    'description': """
        Long description of module's purpose
    """,

    'author': "John Walsh",
    'website': "http://github.com/michaeljohn32",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden/Dependency',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp', 'stock_mts_mto_rule'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
