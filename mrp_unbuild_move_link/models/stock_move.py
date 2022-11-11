from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    origin_mrp_manufacture_move_id = fields.Many2one(
        "stock.move",
        string="Manufacturing order stock move",
        checkcompany=True,
        help="Stock move id of the previous manufacturing order",
    )
