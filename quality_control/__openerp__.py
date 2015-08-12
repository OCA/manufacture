# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c)
#    2010 NaN Projectes de Programari Lliure, S.L. (http://www.NaN-tic.com)
#    2014 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
#    2014 AvanzOsc (http://www.avanzosc.es)
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
    "name": "Quality control",
    "version": "1.0",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Ana Juaristi <ajuaristio@gmail.com>",
    ],
    "category": "Quality control",
    "depends": [
        'product',
    ],
    "data": [
        'data/quality_control_data.xml',
        'security/quality_control_security.xml',
        'security/ir.model.access.csv',
        'wizard/qc_test_wizard_view.xml',
        'views/qc_menus.xml',
        'views/qc_inspection_view.xml',
        'views/qc_test_category_view.xml',
        'views/qc_test_view.xml',
        'views/qc_trigger_view.xml',
        'views/product_template_view.xml',
        'views/product_category_view.xml',
    ],
    "demo": [
        'demo/quality_control_demo.xml',
    ],
    "installable": True,
}
