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

    @api.depends("move_finished_ids.move_line_ids")
    def _compute_finished_backorders(self):
        for production in self:
            production.finished_move_from_backorder_ids = self.env["stock.move.line"]
            backorders = production.procurement_group_id.mrp_production_ids
            for backorder in backorders:
                backorder.mapped("finished_move_line_ids").production_id = backorder
                production.finished_move_from_backorder_ids |= (
                    backorder.finished_move_line_ids
                )
