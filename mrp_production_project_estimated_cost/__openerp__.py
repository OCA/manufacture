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
    "name": "Estimated costs in manufacturing orders",
    "version": "1.0",
    "category": "Manufacturing",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "depends": [
        "product",
        "analytic",
        "mrp",
        "mrp_operations_extension",
        "mrp_project_link",
        "product_variant_cost"
    ],
    "data": [
        "data/analytic_journal_data.xml",
        "data/fictitious_mrp_production_sequence.xml",
        "wizard/wiz_create_fictitious_of_view.xml",
        "views/account_analytic_line_view.xml",
        "views/mrp_production_view.xml",
        "views/product_view.xml",
        "views/mrp_bom_view.xml"
    ],
    "installable": True,
}
