# Copyright 2015 Nicola Malcontenti - Agile Business Group
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Repair Discount",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "Agile Business Group, " "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["repair"],
    "data": [
        "views/mrp_repair_view.xml",
        "report/repair_templates_repair_order.xml",
    ],
    "installable": True,
}
