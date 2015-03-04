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
    'author': 'Elico Corp, Odoo Community Association (OCA)',
    'website': 'www.openerp.net.cn',
    'category': 'Generic Modules/Production',
    'depends': ['procurement', 'sale', 'mrp', 'purchase'],
    'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Module Description
==================
Procurement Improvement - supply method

This module aims to add more flexibility on procurement management.
  * Allowing planner changing the supply method on the procurement order level by
        adding a new field supply_method for planner to modify.

  * Allowing planner changing the procurement method and supply method
        before the procurement order is running.

Business case:
    One company might purchase from one company or produce in another company
        for the same product, the planner can change the supply method
        on the procurement order level instead of having two products with different
        supply methods.

Please note that this module re-define the field: procure_method
    which is defined in module: procurement.

Installation
============

To install this module, you need to:

 * have basic modules installed (sale, mrp, procurement, purchase)

Configuration
=============

To configure this module, you need to:

 * No specific configuration needed.

Usage
=====


For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================


Credits
=======


Contributors
------------

* Alex Duan <alex.duan@elico-corp.com>

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
    'data': [
        'procurement_supply_method_views.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
