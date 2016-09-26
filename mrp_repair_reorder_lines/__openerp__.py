# -*- coding: utf-8 -*-
# Copyright 2016 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Repair Lines with sequence number",
    "summary": '''
    Provide a new field on the repair line form, allowing to manage the lines
    order.''',
    "version": "8.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://www.agilebg.org/",
    "author": "Agile Business Group,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mrp_repair"],
    "data": ["views/repair_view.xml"]
}
