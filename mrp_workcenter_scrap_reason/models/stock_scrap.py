# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import ValidationError


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    @api.depends("workorder_id.workcenter_id")
    def _compute_allowed_reason_code_ids(self):
        res = super()._compute_allowed_reason_code_ids()
        codes = self.env["scrap.reason.code"]
        for rec in self:
            domain = []
            if rec.product_id:
                domain += [
                    "|",
                    ("product_category_ids", "=", False),
                    ("product_category_ids", "in", rec.product_id.categ_id.id),
                ]
            if rec.workorder_id:
                domain += [
                    "|",
                    ("mrp_workcenter_ids", "=", False),
                    ("mrp_workcenter_ids", "in", rec.workorder_id.workcenter_id.id),
                ]
            rec.allowed_reason_code_ids = codes.search(domain)
        return res

    @api.constrains("reason_code_id", "product_id", "workorder_id")
    def _check_reason_code_id(self):
        for rec in self:
            if (
                rec.reason_code_id
                and rec.reason_code_id not in rec.allowed_reason_code_ids
            ):
                raise ValidationError(
                    self.env._(
                        "The selected reason code is not allowed for this "
                        "product category or work center"
                    )
                )
        return super()._check_reason_code_id()
