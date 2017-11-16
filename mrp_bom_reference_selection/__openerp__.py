# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
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
    'name': 'Bill of Material Selection Reference',
    'version': '8.0.1.1.0',
    'author': 'Savoir-faire Linux',
    'license': 'AGPL-3',
    'category': 'Others',
    'summary': 'Bill of Material Selection Reference',
    'depends': [
        'mrp',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_bom_view.xml',
        'views/mrp_product_produce_view.xml',
        'views/stock_production_lot_view.xml',
    ],
    'post_init_hook': 'set_bill_of_material_references',
    'installable': False,
    'application': True,
}
