# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Repair Picking",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "category": "Repair",
    "website": "https://github.com/OCA/manufacture",
    "summary": "Enhanced repair order management with pickings "
    "for adding and removing components",
    "depends": ["repair", "stock_move_forced_lot", "repair_stock_move"],
    "data": [
        "views/stock_warehouse_views.xml",
        "views/repair_order_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
