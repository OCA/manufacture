# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    lot_producing_id = fields.Many2one(compute="_compute_lot_producing_id")

    @api.depends("move_finished_ids.restrict_lot_id")
    def _compute_lot_producing_id(self):
        for order in self:
            order.lot_producing_id = order.move_finished_ids.filtered(
                lambda m: m.product_id == order.product_id
            ).restrict_lot_id
