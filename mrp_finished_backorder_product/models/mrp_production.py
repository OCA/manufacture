# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    finished_move_from_backorder_ids = fields.One2many(
        "stock.move.line",
        compute="_compute_finished_backorders",
        string="Finished Backorders",
    )

    @api.depends(
        "production_group_id.production_ids.move_finished_ids.move_line_ids.state"
    )
    def _compute_finished_backorders(self):
        for production in self:
            orders = production.production_group_id.production_ids
            production.finished_move_from_backorder_ids = (
                orders.move_finished_ids.move_line_ids.filtered(
                    lambda line: line.state == "done"
                )
            )
