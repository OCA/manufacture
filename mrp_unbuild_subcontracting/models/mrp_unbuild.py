from odoo import fields, models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    picking_id = fields.Many2one("stock.picking", "Transfer", readonly=True)
    is_subcontracted = fields.Boolean("Is Subcontracted", readonly=True)
