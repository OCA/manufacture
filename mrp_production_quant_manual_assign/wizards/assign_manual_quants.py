# Copyright 2021 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class AssignManualQuants(models.TransientModel):
    _inherit = "assign.manual.quants"

    mo_id = fields.Many2one(related="move_id.raw_material_production_id")

    @api.model
    def _prepare_wizard_line(self, move, quant):
        line = super()._prepare_wizard_line(move, quant)
        if move.raw_material_production_id:
            move_lines = move.move_line_ids.filtered(
                lambda ml: (
                    ml.location_id == quant.location_id
                    and ml.lot_id == quant.lot_id
                    and ml.owner_id == quant.owner_id
                    and ml.package_id == quant.package_id
                )
            )
            line["to_consume_now"] = bool(any(move_lines.mapped("picked")))
        return line

    def assign_quants(self):
        res = super().assign_quants()
        if self.mo_id:
            precision_digits = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            for ml in self.move_id.move_line_ids:
                quants = self.quants_lines.filtered(
                    lambda quant_line: quant_line.lot_id == ml.lot_id  # noqa: B023
                    and quant_line.selected
                    and quant_line.location_id == ml.location_id  # noqa: B023
                )
                ml.quantity = sum([quant.qty for quant in quants])
                ml.picked = all([quant.to_consume_now for quant in quants])
                if float_is_zero(ml.quantity, precision_digits=precision_digits):
                    ml.unlink()
            if not any(ml.picked for ml in self.move_id.move_line_ids):
                self.move_id.picked = False
        return res


class AssignManualQuantsLines(models.TransientModel):
    _inherit = "assign.manual.quants.lines"

    to_consume_now = fields.Boolean()

    @api.onchange("selected")
    def _onchange_selected(self):
        res = super()._onchange_selected()
        for rec in self:
            if not rec.selected:
                rec.to_consume_now = False
        return res
