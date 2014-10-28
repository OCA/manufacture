# -*- encoding: utf-8 -*-
##############################################################################
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
{
    "name": "MRP BoM Version",
    "version": "1.0",
    "author": "OdooMRP team",
    "category": "Manufacturing",
    "website": "http://www.odoomrp.com",
    "description": """
    This module performs the following:

    1.- In the MRP BoM list object, 2 new fields are added:

        1.1.- Historical Date, of type date.
        1.2.- Status, of type selection, with these values: draft, in active
              and historical. This new field has gotten because it has added a
              workflow to MRP BoM list object.

    You can only modify the components and / or production process if it is in
    draft status. The other fields can only be changed if they are not in
    historical state.
    when the MRP BoM list is put to active, a record of who has activated,
    and when will include in chatter/log.
    Also creates a constraint for the sequence field to be unique.
    """,
    "depends": ['mrp',
                ],
    "data": ['data/mrp_bom_data.xml',
             'views/mrp_bom_view.xml',
             ],
    "installable": True
}
