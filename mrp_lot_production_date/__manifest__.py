# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "MRP Lot Production Date",
    "Summary": "Set a production date automatically on produced lots/SN.",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": [
        # core
        "mrp",
        # OCA/stock-logistics-workflow
        "stock_lot_production_date",
    ],
    "installable": True,
    "auto_install": True,
    "license": "AGPL-3",
}
