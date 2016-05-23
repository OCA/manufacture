# -*- coding: utf-8 -*-
# (c) 2014-2015 Avanzosc
# (c) 2014-2015 Pedro M. Baeza
# (c) 2015 Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Estimated costs in manufacturing orders",
    "version": "8.0.1.2.0",
    "category": "Manufacturing",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Antiun Ingenería S.L.,"
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "depends": [
        "mrp_operations_project",
    ],
    "data": [
        "data/analytic_journal_data.xml",
        "data/virtual_mrp_production_sequence.xml",
        "wizard/wiz_create_virtual_mo_view.xml",
        "views/account_analytic_line_view.xml",
        "views/mrp_production_view.xml",
        "views/product_view.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
