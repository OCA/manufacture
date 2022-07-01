from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    is_subcontractor = fields.Boolean()
