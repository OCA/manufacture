# Copyright 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QualityControlIssue(models.Model):
    _inherit = "qc.issue"

    repair_order_ids = fields.One2many(
        comodel_name="repair.order",
        string="Repair Orders",
        inverse_name="qc_issue_id",
    )
    repair_order_count = fields.Integer(
        compute="_compute_repair_order_count",
    )

    @api.multi
    def _compute_repair_order_count(self):
        for issue in self:
            issue.repair_order_count = len(issue.repair_order_ids)

    @api.multi
    def action_view_repair_orders(self):
        action = self.env.ref("repair.action_repair_order_tree")
        result = action.read()[0]
        result["domain"] = [("id", "in", self.repair_order_ids.ids)]
        return result
