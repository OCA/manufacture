# -*- coding: utf-8 -*-
# Copyright 2016 Nicola Malcontenti
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mrp Repair Payment Terms",
    "summary": '''
    Add new field Payment term on repair order
    ''',
    "version": "8.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://www.agilebg.org/",
    "author": "Agile Business Group,"
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["mrp_repair"],
    "data": ["views/mrp_repair_payment_terms.xml"],
}
