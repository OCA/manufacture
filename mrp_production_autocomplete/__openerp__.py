# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) All Rights Reserved 2014 Akretion
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
    'name': 'Production AutoComplete',
    'version': '0.1',
    'author': 'Akretion',
    'maintener': 'Akretion',
    'category': 'Manufaturing',
    'summary': "Set as Done Manufacturing Orders with cron",
    'depends': [
        'mrp',
    ],
    'description': """
Production AutoComplete
==========================
This module will set in done all manufacturing Order for the product
which have the option "Complete Manuf. Order" tic.
The validation is done by a scheduled action.

A case of use is when for example you have an external system to manage the
production, and this system can not trigger when the manufacturing order have
been done. In this case you can automatically set the production order in done
and then you can still use odoo for computing the consomation of goods and for
processing the move for the picking.

Contributors
------------
* David BEAL <david.beal@akretion.com>

""",
    'website': 'http://www.akretion.com/',
    'data': [
        'cron_data.xml',
        'product_view.xml',
    ],
    'demo': [
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
