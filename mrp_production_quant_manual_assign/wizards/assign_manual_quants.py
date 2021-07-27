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
    def default_get(self, fields):
        res = super(AssignManualQuants, self).default_get(fields)
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
            line["qty_done"] = sum(move_lines.mapped("qty_done"))
            line["to_consume_now"] = bool(line["qty_done"])
        return line

    def assign_quants(self):
        res = super(AssignManualQuants, self).assign_quants()
        move = self.move_id
        if self._is_production_single_lot(move):
            precision_digits = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            lots_to_consume = self.quants_lines.filtered(
                lambda l: l.to_consume_now
            ).mapped("lot_id")
            for ml in move.move_line_ids:
                if ml.lot_id in lots_to_consume:
                    ml.qty_done = ml.product_qty
                elif float_is_zero(ml.product_qty, precision_digits=precision_digits):
                    ml.unlink()
                else:
                    ml.qty_done = 0.0
        return res


class AssignManualQuantsLines(models.TransientModel):
    _inherit = "assign.manual.quants.lines"

    to_consume_now = fields.Boolean()
    qty_done = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
    )
