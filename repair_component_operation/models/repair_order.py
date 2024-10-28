# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import _, api, fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    scrap_ids = fields.One2many("stock.scrap", "repair_id")
    scrap_count = fields.Integer(compute="_compute_scrap_count")

    @api.depends("scrap_ids")
    def _compute_scrap_count(self):
        for rec in self:
            rec.scrap_count = len(rec.scrap_ids)

    def button_open_scrap(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
        action["domain"] = [("repair_id", "=", self.id)]
        action["context"] = dict(self._context, default_origin=self.name)
        return action

    def button_operate_components(self):
        return {
            "name": _("Operate Component"),
            "view_mode": "form",
            "res_model": "repair.component.operate",
            "view_id": self.env.ref(
                "repair_component_operation.view_repair_component_operate_form"
            ).id,
            "type": "ir.actions.act_window",
            "context": {
                "default_repair_id": self.id,
                "product_ids": self.operations.filtered(
                    lambda rl: rl.type == "add"
                ).move_id.move_line_ids.product_id.mapped("id"),
                "lot_ids": self.operations.filtered(
                    lambda rl: rl.type == "add"
                ).move_id.move_line_ids.lot_id.mapped("id"),
            },
            "target": "new",
        }
