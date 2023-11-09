# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    lock_planning = fields.Boolean(
        help="If set, any change to the planning will be restricted",
        readonly=True,
    )

    @api.constrains("lock_planning")
    def _check_lock_planning(self):
        for workorder in self:
            if not workorder.lock_planning:
                continue
            if not (workorder.date_planned_start and workorder.date_planned_finished):
                raise ValidationError(
                    _("Cannot lock planning of workorder if workorder is not planned")
                )

    @api.constrains(
        "date_planned_start",
        "date_planned_finished",
        "duration_expected",
        "workcenter_id",
    )
    def _check_lock_planning_fields(self):
        for workorder in self:
            if not workorder.lock_planning:
                continue
            raise ValidationError(
                _(
                    "Workorder is locked and modification of Scheduled dates, "
                    "Expected duration or Workcenter is not allowed. "
                    "Please unlock the planning first."
                )
            )

    def toggle_lock_planning(self):
        self.ensure_one()
        self.lock_planning = not self.lock_planning
