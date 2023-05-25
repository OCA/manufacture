# Copyright 2022-23 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class MrpComponentOperate(models.Model):
    _inherit = "mrp.component.operate"

    scrap_reason_code_id = fields.Many2one(
        comodel_name="scrap.reason.code",
        string="Scrap Reason Code",
        domain="[('id', 'in', allowed_reason_code_ids)]",
    )
    allowed_reason_code_ids = fields.Many2many(
        comodel_name="scrap.reason.code",
        compute="_compute_allowed_reason_code_ids",
    )

    @api.depends("product_id")
    def _compute_allowed_reason_code_ids(self):
        for rec in self:
            codes = self.env["scrap.reason.code"]
            if rec.product_id:
                codes = codes.search(
                    [
                        "|",
                        ("product_category_ids", "=", False),
                        ("product_category_ids", "in", rec.product_id.categ_id.id),
                    ]
                )
            rec.allowed_reason_code_ids = codes

    def _create_scrap(self):
        scrap = super()._create_scrap()
        scrap.reason_code_id = self.scrap_reason_code_id
        return scrap
