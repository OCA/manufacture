# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    type_id = fields.Many2one(comodel_name="qc.inspection.type")

    @api.model_create_multi
    def create(self, vals_list):
        qc_type_model = self.env["qc.inspection.type"]
        for vals in vals_list:
            if vals.get("name", "/") == "/" and vals.get("type_id"):
                qc_type = qc_type_model.browse(vals["type_id"])
                if qc_type.sequence_id:
                    vals["name"] = qc_type.sequence_id.next_by_id(
                        sequence_date=vals.get("date")
                    )
        return super().create(vals_list)
