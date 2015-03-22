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
    'author': 'Akretion,Odoo Community Association (OCA)',
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

A case of use is when you have an external system to manage the production,
but this system can not trigger when the manufacturing order have been done.
So as you still want to manage the consumation of goods and the processing of
move for the picking, You can automatically set the production order in done
with a schedule action.


Configuration
=============

To use this module, you need to go to:
* Sale > Product
    - You can tic the box "Complete Manuf. Order" to select autocomplete product
* Setting > Scheduler > Scheduled Actions
    - You can confirgure the cron "Manuf. Order Auto Complete"

Usage
=====

Nothing to do manufacturing order will be set as done automatically


Credits
=======

Contributors
------------
* David BEAL <david.beal@akretion.com>

Maintainer
----------
.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
      :target: http://odoo-community.org
      This module is maintained by the OCA.
      OCA, or the Odoo Community Association, is a nonprofit organization
      whose mission is to support the collaborative development of Odoo features
      and promote its widespread use.
      To contribute to this module, please visit http://odoo-community.org.

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
