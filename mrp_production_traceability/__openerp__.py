
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 25/08/2014
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
    'name': 'MRP Production Traceability',
    'version': "1.0",
    'category': "Generic Modules",
    'description': """
    This modules adds component traceability in production orders.
    """,
    'author': 'OdooMRP team',
    'contributors': ["Daniel Campos <danielcampos@avanzosc.es>"],
    'website': "http://www.odoomrp.com",
    'depends': ["mrp"],
    'data': ["views/stock_move_view.xml"],
    'installable': True,
}
