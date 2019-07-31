# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP Stock Orderpoint Manual Procurement",
    "summary": "Updates the value of MO Responsible and keeps track"
               "of changes regarding this field",
    "version": "12.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": [
        "mrp",
        "stock_orderpoint_manual_procurement",
    ],
    "data": [
        "views/mrp_production_view.xml",
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
    'auto_install': True
}
