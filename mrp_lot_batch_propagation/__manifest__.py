# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "MRP Lot Batch Propagation",
    "summary": "Track BOM information through manufacturing batches"
    " for quality control",
    "version": "17.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": [
        "mrp",
        "stock",
    ],
    "data": [
        "views/product_category.xml",
        "views/product_template.xml",
        "views/stock_lot.xml",
        "views/mrp_production.xml",
    ],
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}
