# -*- coding: utf-8 -*-
# © 2015 Avanzosc
# © 2015 Pedro M. Baeza
# © 2015 Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP Operations Time Control",
    "version": "8.0.1.1.0",
    "depends": [
        "mrp_operations_extension",
    ],
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Antiun Ingeniería S.L., "
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Mikel Arregi <mikelarregi@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>"
    ],
    "category": "Manufacturing",
    'data': [
        "views/operation_time_view.xml",
        "views/mrp_production_view.xml",
        "security/ir.model.access.csv",
        "data/mrp_production_workcenter_line_workflow.xml"
    ],
    "installable": True,
}
