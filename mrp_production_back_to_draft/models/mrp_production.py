# Copyright 2024 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_return_to_draft(self):
        self._check_company()
        for rec in self:
            if rec.state not in ["confirmed", "cancel"]:
                raise UserError(
                    _(
                        "You cannot return to draft the following MO: %s. "
                        "Only confirmed or cancelled MO can be returned to draft."
                    )
                    % rec.name
                )
            else:
                (rec.move_raw_ids + rec.move_finished_ids)._action_cancel()
                (rec.move_raw_ids + rec.move_finished_ids).write({"state": "draft"})
                rec.workorder_ids.write({"state": "waiting"})
                if rec.state != "draft":
                    raise UserError(
                        _("Could not set the production order back to draft")
                    )

    @api.depends("move_raw_ids.state", "move_finished_ids.state")
    def _compute_state(self):
        super()._compute_state()
        for production in self:
            if (
                production.state == "cancel"
                and all(m.state == "draft" for m in production.move_raw_ids)
                and all(m.state == "draft" for m in production.move_finished_ids)
            ):
                production.state = "draft"
        return
