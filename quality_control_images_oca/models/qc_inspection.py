# Copyright 2025 Edilio Escalona Almira - Binhexteam
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    enable_image = fields.Boolean(related="test.enable_image")
    is_required_image = fields.Boolean(related="test.is_required_image")

    def action_confirm(self):
        inspection = super().action_confirm()
        for rec in self:
            if rec.is_required_image:
                all_questions_invalid = rec.inspection_lines.filtered(
                    lambda x: x.success is False and not x.image_1920
                )
                if all_questions_invalid:
                    raise ValidationError(
                        _(
                            "The following question(s) are not satisfactory, "
                            "so an image must be attached. \n {}"
                        ).format(", ".join(all_questions_invalid.mapped("name")))
                    )
        return inspection
