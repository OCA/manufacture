# Copyright 2021 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class AssignManualQuants(models.TransientModel):
    _inherit = "assign.manual.quants"

    is_production_single_lot = fields.Boolean()

    def _is_production_single_lot(self, move):
        mo = move.raw_material_production_id
        if not mo:
            return False
        if mo.product_id.tracking == "serial":
            return True
        return False

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        move = self.env["stock.move"].browse(self.env.context["active_id"])
        res.update({"is_production_single_lot": self._is_production_single_lot(move)})
        return res

    @api.model
    def _prepare_wizard_line(self, move, quant):
        line = super()._prepare_wizard_line(move, quant)
        if self._is_production_single_lot(move):
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
        move = self.move_id
        if self._is_production_single_lot(move):
            precision_digits = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            lots_to_consume = self.quants_lines.filtered(
                lambda quant_line: quant_line.to_consume_now
            ).mapped("lot_id")
            for ml in move.move_line_ids:
                if ml.lot_id in lots_to_consume or ml.product_id.tracking == "none":
                    quants = self.quants_lines.filtered(
                        lambda quant_line: quant_line.lot_id == ml.lot_id and quant_line.selected
                    )
                    ml.picked = all([quant.to_consume_now for quant in quants])
                    ml.quantity = sum([quant.qty for quant in quants])
                elif float_is_zero(ml.quantity, precision_digits=precision_digits):
                    ml.unlink()
        return res


class AssignManualQuantsLines(models.TransientModel):
    _inherit = "assign.manual.quants.lines"

    to_consume_now = fields.Boolean()
