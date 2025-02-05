# Copyright 2025 Edilio Escalona Almira - Binhexteam
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    attachment_ids = fields.One2many(
        "ir.attachment", "qc_inspection_id", string="Attachments"
    )
    is_required_attachment = fields.Boolean(related="test.is_required_attachment")

    def _check_is_required_attachment(self):
        context = dict(self.env.context)
        if not context.get("qc_inspection_set_test", False):
            for rec in self:
                if rec.is_required_attachment:
                    if not rec.attachment_ids:
                        raise ValidationError(
                            _("You must add at least one attachment.")
                        )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self._check_is_required_attachment()
        return res

    def write(self, vals):
        res = super().write(vals)
        self._check_is_required_attachment()
        return res
