# -*- coding: utf-8 -*-
# © 2016 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Sale Info",
    "summary": "Adds sale information to Manufacturing models",
    "version": "9.0.1.0.0",
    "category": "Manufacturing",
    "website": "http://www.antiun.com",
    "author": "AvanzOSC, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp_operations",
        "sale_mrp",
        "sale_order_dates",
        "stock"
    ],
    "data": [
        "views/mrp_production.xml",
        "views/mrp_production_workcenter_line.xml"
    ]
}
