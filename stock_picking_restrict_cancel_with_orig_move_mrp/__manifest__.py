# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking Restrict Cancel with Original Moves",
    "summary": "Restrict cancellation of dest moves according to origin.",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/manufacture",
    "author": "Sergio Corato, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": [
        "sale_mrp",
        "stock_picking_restrict_cancel_with_orig_move",
    ],
}
