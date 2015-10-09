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
    "name": "MRP real costs",
    "version": "1.0",
    "depends": ["analytic",
                "project_timesheet",
                "mrp_project_link",
                "mrp_operations_time_control",
                "stock_account",
                "product_variant_cost",
                "mrp_production_project_estimated_cost"],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "category": "MRP",
    'data': [
        "data/analytic_journal_data.xml",
        "views/mrp_production_view.xml",
        "views/res_config_view.xml"
        ],
    'installable': True,
    'auto_install': False,
}
