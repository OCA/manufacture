# -*- encoding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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
    'name': 'Industrial design specification in BoM',
    'version': '1.0',
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    'license': 'AGPL-3',
    'category': 'Specific Industry Applications',
    'depends': ['mrp'],
    "data": ['mrp_industrial_design.xml'],
    'description': """
This module adds the fields 'Bubble Number' and 'RefDes' (reference description) to a component in BoM view.

It also point the BOM Structure report to a new version that uses the new fields.
""",
    'auto_install': False,
    'installable': False
}
