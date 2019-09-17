# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Repair Refurbish",
    "summary": "Create refurbished products during repair",
    "version": "12.0.1.1.2",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'repair',
    ],
    "data": [
        "views/repair_view.xml",
        "data/stock_data.xml",
        "views/product_template_view.xml",
        "views/product_product_view.xml",
    ],
}
