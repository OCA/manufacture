# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
    "name": "MRP BOM Hierarchy",
    "version": "1.0",
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "description": """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

MRP BOM Hierarchy
=================

This module was written to extend the functionality of Bill of
Materials to support users to better maintain the BOM hierarchy.

This module replaces the existing BOM tree views with a new one, from
which the user can create a complete BOM hierarchy.

The user can navigate from the  tree view to child BOM's, or to the
product's BOM components with a single click.

The user can now search using the field 'Complete Reference' (or Name) to
find all the BOM hierarchy associated to a particular BOM Reference (or
Name) at once.


Installation
============

No specific installation steps are required.

Configuration
=============

No specific configuration steps are required.

Usage
=====

To use this module, you need to go to 'Manufacturing | Products | Bill of
Materials Hierarchy'

Known issues / Roadmap
======================

No issues have been identified with this module.

Credits
=======

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>

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
    "website": "http://www.eficent.com/",
    "license": "AGPL-3",
    "demo": [], 
    "data": [
        "view/mrp.xml",
    ], 
    "test": [],
    "installable": True, 
    "auto_install": False, 
    "active": False
}