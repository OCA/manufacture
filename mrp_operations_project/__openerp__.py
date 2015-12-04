# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP Project Link (with operations)",
    "summary": "Create task for work orders with operators",
    "version": "8.0.1.0.0",
    "depends": [
        "mrp_project",
        "mrp_operations_extension",
    ],
    'license': 'AGPL-3',
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "Antiun Ingeniería,"
              "Odoo Community Association (OCA)",
    "category": "Manufacturing",
    'data': [
        "views/mrp_production_view.xml",
        "views/project_task_view.xml",
    ],
    'installable': True,
    'auto_install': True,
}
