
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "MRP Operations Extension",
    "version": "1.0",
    "description": """
This module adds:

    - New table to store operations to avoid typing them again.
    - Adds a relation from WorkcenterLines to BOM Lists.
    - Adds a relation from WorkcenterLines to Manufacturing Orders in
    Scheduled/Consumed/Finished Products.
    - Adds a relation between Routing Work Center Lines and Work Center extra
    Info.

    """,
    "category": "Manufacturing",
    "data": ['wizard/mrp_workorder_produce_view.xml',
             'views/mrp_workcenter_view.xml',
             'views/mrp_routing_operation_view.xml',
             'views/mrp_production_view.xml',
             'views/mrp_bom_view.xml',
             'views/mrp_routing_workcenter_view.xml',
             'security/ir.model.access.csv'
             ],
    "author": "OdooMRP team",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Daniel Campos <danielcampos@avanzosc.es>",
        "Mikel Arregi <mikelarregi@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "depends": [
        "mrp_operations",
        "mrp",
        "stock",
    ],
    "data": [
        "wizard/mrp_workorder_produce_view.xml",
        "views/mrp_workcenter_view.xml",
        "views/mrp_routing_operation_view.xml",
        "views/mrp_production_view.xml",
        "views/mrp_bom_view.xml",
        "views/mrp_routing_workcenter_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True
}
