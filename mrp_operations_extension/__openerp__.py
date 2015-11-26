# -*- coding: utf-8 -*-
# (c) 2014-2015 Avanzosc
# (c) 2014-2015 Pedro M. Baeza
# (c) 2015 Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Manufacturing Operations Extension",
    "version": "8.0.2.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Antiun Ingeniería S.L., "
              "Odoo Community Association (OCA)",
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
    "images": [
        'images/operation.png',
        'images/routing.png',
        'images/routing_line.png',
        'images/bom.png',
        'images/manufacturing_order.png',
        'images/work_order.png',
        'images/work_order2.png',
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
