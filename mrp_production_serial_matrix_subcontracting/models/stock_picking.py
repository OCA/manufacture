# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    show_subcontract_serial_matrix = fields.Boolean(
        compute="_compute_show_subcontract_serial_matrix",
    )

    def _get_subcontract_serial_matrix_productions(self):
        self.ensure_one()
        productions = self.move_ids.filtered(
            "is_subcontract"
        )._get_subcontract_production()
        return productions.filtered(
            lambda p: p.show_serial_matrix
            and p.state not in ("draft", "cancel", "done")
        )

    def _compute_show_subcontract_serial_matrix(self):
        for rec in self:
            rec.show_subcontract_serial_matrix = bool(
                rec._get_subcontract_serial_matrix_productions()
            )

    def action_open_subcontract_serial_matrix(self):
        self.ensure_one()
        productions = self._get_subcontract_serial_matrix_productions()
        if not productions:
            raise UserError(
                _("No subcontracted MO with serial-tracked product on this transfer.")
            )
        matrix_obj = self.env["mrp.production.serial.matrix"]
        matrices = matrix_obj
        for production in productions:
            matrix = matrix_obj.search([("production_id", "=", production.id)], limit=1)
            if not matrix:
                matrix = matrix_obj.create({"production_id": production.id})
            matrix.subcontract_receipt_picking_id = self
            matrices |= matrix
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp_production_serial_matrix.action_mrp_production_serial_matrix"
        )
        if len(matrices) == 1:
            action.update(
                {
                    "res_id": matrices.id,
                    "views": [
                        (
                            self.env.ref(
                                "mrp_production_serial_matrix."
                                "mrp_production_serial_matrix_view_form"
                            ).id,
                            "form",
                        )
                    ],
                }
            )
        else:
            action.update(
                {
                    "domain": [("id", "in", matrices.ids)],
                    "context": {},
                }
            )
        return action
