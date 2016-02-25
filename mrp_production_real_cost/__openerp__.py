# -*- coding: utf-8 -*-
# © 2014-2015 Avanzosc
# © 2014-2015 Antiun Ingeniería
# © 2014-2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Real costs in manufacturing orders",
    "version": "8.0.1.0.2",
    "depends": [
        "project_timesheet",
        "mrp_project",
        "mrp_operations_extension",
        "mrp_operations_time_control",
        "stock_account",
    ],
    'license': 'AGPL-3',
    "images": [],
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Antiun Ingeniería S.L., "
              "Odoo Community Association (OCA)",
    "category": "Manufacturing",
    'data': [
        "data/analytic_journal_data.xml",
        "views/mrp_production_view.xml",
    ],
    'demo': [
        'demo/mrp_production_demo.xml',
    ],
    'installable': True,
}
