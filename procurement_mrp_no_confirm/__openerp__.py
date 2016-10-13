# -*- coding: utf-8 -*-
# © 2015 AvanzOSC
# © 2015 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Procurement MRP no Confirm",
    "version": "8.0.1.0.0",
    "depends": ["mrp"],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    "category": "MRP",
    "data": ["data/mrp_production_workflow.xml"],
    "installable": True,
    "auto_install": False,
    "uninstall_hook": "uninstall_hook",
}
