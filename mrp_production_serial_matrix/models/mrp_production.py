# Copyright 2021 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    show_serial_matrix = fields.Boolean(compute="_compute_show_serial_matrix")

    def _compute_show_serial_matrix(self):
        for rec in self:
            rec.show_serial_matrix = rec.product_id.tracking == "serial"

    def action_open_mrp_production_serial_matrix(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp_production_serial_matrix.action_mrp_production_serial_matrix"
        )
        serial_matrix = self.env["mrp.production.serial.matrix"].search(
            [("production_id", "=", self.id)], limit=1
        )
        if not serial_matrix:
            serial_matrix = self.env["mrp.production.serial.matrix"].create(
                {
                    "production_id": self.id,
                }
            )
        action.update(
            {
                "res_id": serial_matrix.id,
                "views": [
                    (
                        self.env.ref(
                            "mrp_production_serial_matrix.mrp_production_serial_matrix_view_form"
                        ).id,
                        "form",
                    )
                ],
            }
        )
        return action
