# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class MrpProductionSerialMatrix(models.Model):
    _inherit = "mrp.production.serial.matrix"

    subcontract_receipt_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Subcontract Receipt",
        help="Receipt this serial matrix was launched from. The completion "
        "message is posted on it.",
    )

    def _validate_and_get_backorder(self, mo):
        if not mo._get_subcontract_move():
            return super()._validate_and_get_backorder(mo)
        res = mo.subcontracting_record_component()
        if isinstance(res, dict):
            if res.get("type") == "ir.actions.act_window_close":
                return False
            if res.get("res_model") == "mrp.production" and res.get("res_id"):
                return self.env["mrp.production"].browse(res["res_id"])
            raise UserError(
                _(
                    "Something went wrong and the subcontracted MO could not be "
                    "recorded. %s"
                )
                % res
            )
        return False

    def _get_subcontract_receipt_picking(self):
        self.ensure_one()
        if self.subcontract_receipt_picking_id:
            return self.subcontract_receipt_picking_id
        moves = self.production_id._get_subcontract_move()
        pending = moves.filtered(lambda m: m.state not in ("done", "cancel"))
        return (pending or moves).picking_id[:1]

    def _notify_subcontract_completion(self, success=True, error=False):
        self.ensure_one()
        picking = self._get_subcontract_receipt_picking()
        if not picking:
            return
        if success:
            body = _(
                "The serial numbers matrix for %(product)s has finished "
                "successfully."
            ) % {"product": self.product_id.display_name}
        else:
            body = _(
                "The serial numbers matrix for %(product)s ended with an error: "
                "%(error)s"
            ) % {"product": self.product_id.display_name, "error": error}
        picking.message_post(
            body=body,
            author_id=self.env.ref("base.partner_root").id,
            partner_ids=self.env.user.partner_id.ids,
        )

    def _set_matrix_done(self):
        res = super()._set_matrix_done()
        self._notify_subcontract_completion(success=True)
        return res

    def _set_matrix_exception(self, error):
        res = super()._set_matrix_exception(error)
        self._notify_subcontract_completion(success=False, error=error)
        return res
