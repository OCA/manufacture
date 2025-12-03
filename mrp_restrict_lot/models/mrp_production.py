# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    lot_producing_id = fields.Many2one(
        compute="_compute_lot_producing_id",
        inverse="_inverse_lot_producing_id",
        store=True,
        readonly=False,
    )

    @api.depends("move_finished_ids.restrict_lot_id")
    def _compute_lot_producing_id(self):
        for order in self:
            restricted_lot = order.move_finished_ids.filtered(
                lambda m, order=order: m.product_id == order.product_id
            ).restrict_lot_id
            if restricted_lot:
                order.lot_producing_id = restricted_lot

    def _inverse_lot_producing_id(self):
        for order in self:
            move_finished = order.move_finished_ids.filtered(
                lambda m, order=order: m.product_id == order.product_id
            )
            if move_finished:
                move_finished.restrict_lot_id = order.lot_producing_id
