# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ["mrp.production", "tier.validation"]
    _state_from = ["confirmed", "to_close", "progress"]
    _state_to = ["done"]

    _tier_validation_state_field_is_computed = True
    _tier_validation_manual_config = False

    def button_mark_done(self):
        self._check_tier_validation()
        return super().button_mark_done()

    def _check_tier_validation(self):
        for rec in self:
            if rec.need_validation:
                if rec.validation_status != "validated":
                    raise ValidationError(
                        _(
                            "This action needs to be validated for at least "
                            "one record. \nPlease request a validation."
                        )
                    )
            if rec.review_ids and not rec.validated:
                raise ValidationError(
                    _("A validation process is still open for at least one record.")
                )
