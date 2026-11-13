# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ["mrp.production", "base.cancel.confirm"]

    _has_cancel_reason = "optional"  # ["no", "optional", "required"]

    cancel_confirm = fields.Boolean(default=False)

    def action_cancel(self):
        if self.env.context.get("cancel_confirm_wizard") and not self.filtered(
            "cancel_confirm"
        ):
            return self.open_cancel_confirm_wizard()
        return super().action_cancel()
