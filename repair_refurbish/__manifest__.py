# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Repair Refurbish",
    "summary": "Create refurbished products during repair",
    "version": "14.0.1.0.1",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["repair"],
    "data": [
        "views/repair_view.xml",
        "data/stock_data.xml",
        "views/product_template_view.xml",
        "views/product_product_view.xml",
    ],
}
