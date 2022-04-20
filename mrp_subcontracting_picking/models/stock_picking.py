from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    state = fields.Selection(
        selection_add=[("subcontracted", "Subcontracted"), ("waiting",)]
    )
