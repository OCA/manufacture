# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Cost Lot",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "author": "Xtendoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "maintainers": [
        "manuelcalero@xtendoo.es",
    ],
    "development_status": "Beta",
    "data": [
        "views/mrp_production.xml",
        "views/stock_product_lot_view.xml",
    ],
    "depends": [
        "sale",
        "stock",
        "mrp",
    ]
}
