# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
    'name': 'MRP Merge Productions',
    'version': '0.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Manufacturing',
    'summary': 'MRP - Merge Productions',
    'description': """
MRP - Merge Productions
=======================

This module allows merging productions based on the following criteria:
* All productions must be similar:
  * Same BOM
  * Same Product and UOM
  * Same Source and Destination Locations for the products
* The productions must not be in the 'done', 'cancel' or 'in_production' states

This is intented to provide easier handling of large amounts of similar
manufacturing orders created by procurement orders, as it allows collapsing
many similar productions into the same MO.

Contributors
------------
* Vincent Vinet (vincent.vinet@savoirfairelinux.com)
""",
    'depends': [
        'mrp',
        'product',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'merge_productions_view.xml',
    ],
    'demo': [],
    'test': [
        'test/merge_productions.yml',
    ],
    'installable': True,
    'auto_install': False,
}
