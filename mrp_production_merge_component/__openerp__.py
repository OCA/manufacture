# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
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
    'name': "MRP Production merge component",
    'version': '1.0',
    'category': 'Manufacturing',
    'description': """
MRP Production merge component
==============================

This module was written to extend the manufacturing capabilities of Odoo,
and allows manufacturing orders to compute the required components, so that
the same components of the BOM found at different levels of the  hierarchy
are merged into the same manufacturing order line.

This allows for a more optimized procurement process, since all the components
will be ordered in the same Purchase Order Line.

This solution is specific to 7.0. In version 8.0 onwards the procurement
process will merge various procurement orders for the same product and
supplier into the same Purchase Order Line.


Installation
============

No additional installation instructions are required.


Configuration
=============

This module does not require any additional configuration.

Usage
=====

No specific usage instructions are required.

Known issues / Roadmap
======================

No issues have been identified.

Credits
=======

Contributors
------------

* Jordi Ballester <jordi.ballester@eficent.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
""",
    'author': "Eficent,Odoo Community Association (OCA)",
    'website': 'http://www.eficent.com',
    'license': 'AGPL-3',
    "depends": ['mrp'],
    "data": ['mrp_demo.xml'],
    'test': [
        'test/mrp_users.yml',
        'test/order_demo.yml',
    ],
    "demo": [],
    "active": False,
    "installable": True
}
