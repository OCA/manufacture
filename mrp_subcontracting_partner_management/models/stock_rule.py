from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    subcontracor_resuply_id = fields.Many2one(
        comodel_name="res.partner",
    )
