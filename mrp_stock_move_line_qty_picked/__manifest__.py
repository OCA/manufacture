# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.

{
    "name": "MRP Stock Move Line Qty Picked",
    "summary": "Adapt functionality of stock_move_line_qty_picked into MRP",
    "version": "18.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp", "stock_move_line_qty_picked"],
    "data": ["views/mrp_production.xml"],
}
