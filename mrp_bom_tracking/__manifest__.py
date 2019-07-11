# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "MRP BoM Tracking",
    "version": "12.0.1.0.0",
    "author": "Eficent, Odoo Community Association (OCA)",
    "summary": "Logs any change to a BoM in the chatter",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/bom_template.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
