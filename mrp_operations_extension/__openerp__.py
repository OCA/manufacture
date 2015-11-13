
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
    "version": "8.0.1.1.0",
    "category": "Manufacturing",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Daniel Campos <danielcampos@avanzosc.es>",
        "Mikel Arregi <mikelarregi@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "depends": [
        "mrp_operations",
        "mrp_hook",
        "stock",
        "hr_timesheet",
    ],
    "data": [
        "data/mrp_operations_extension_data.xml",
        "wizard/mrp_workorder_produce_view.xml",
        "views/mrp_workcenter_view.xml",
        "views/mrp_routing_operation_view.xml",
        "views/mrp_production_view.xml",
        "views/mrp_bom_view.xml",
        "views/mrp_routing_view.xml",
        "views/res_config_view.xml",
        "security/ir.model.access.csv",
        "security/mrp_operations_extension_security.xml",
    ],
    "demo": [
        "demo/res_partner_demo.xml",
        "demo/hr_employee_demo.xml",
        "demo/mrp_workcenter_demo.xml",
        "demo/mrp_bom_demo.xml",
        "demo/mrp_routing_demo.xml",
        "demo/mrp_production_demo.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True
}
