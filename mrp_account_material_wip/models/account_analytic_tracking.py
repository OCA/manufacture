# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AnalyticTrackingItem(models.Model):
    _inherit = "account.analytic.tracking.item"

    stock_move_id = fields.Many2one(
        "stock.move", string="Stock Move", ondelete="restrict"
    )

    def _compute_name(self):
        super()._compute_name()
        for tracking in self.filtered("stock_move_id"):
            move = tracking.stock_move_id
            tracking.name = "{} / {}".format(
                move.raw_material_production_id.display_name,
                move.product_id.display_name,
            )

    @api.depends("manual_planned_amount", "stock_move_id")
    def _compute_planned_amount(self):
        super()._compute_planned_amount()
        for tracking in self.filtered("stock_move_id"):
            move = tracking.stock_move_id
            qty = move.product_uom_qty
            unit_cost = move.product_id.standard_price
            tracking.planned_amount += qty * unit_cost
