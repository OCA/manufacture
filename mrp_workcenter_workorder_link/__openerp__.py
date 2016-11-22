# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) All Rights Reserved 2015 Akretion
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
    'name': 'MRP Workcenter Workorder Link',
    'version': '0.5',
    'author': 'Akretion',
    'summary': "Switch easily between Work Centers and Work Orders",
    'maintener': 'Akretion',
    'category': 'Manufacturing',
    'depends': [
        'mrp_operations',
    ],
    'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

MRP Workcenter Workorder Link
=============================


* Add a button on work order list view to quickly jump into work center
* Add a button on work center tree view to quickly jump into work orders
  using this work center
* Display linked work orders in work center form tab


Configuration
=============

To visualize features offered by this module, you need to:

 * go to Settings > Configuration > Manufacturing
 * in the section Manufacturing Order / Planning,
   check "Manage routings and work orders" and Validate

Usage
=====

To use this module, you need to go to:

 * Manufacturing > Manufacturing > Work Orders
 * Manufacturing > Configuration > Work Centers


Credits
=======

Contributors
------------

* David BEAL <david.beal@akretion.com>
* Sébastien BEAU <sebastien.beau@akretion.com>

Icon
----
Patricia Clausnitzer: Creative Commons


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
        'mrp_view.xml',
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
