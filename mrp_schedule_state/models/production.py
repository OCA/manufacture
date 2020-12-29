#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>

from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = ["mrp.production", "selection.rotate.mixin"]
    _name = "mrp.production"

    @api.model
    def _get_schedule_states(self):
        return self._set_schedule_states()

    date_planned_start = fields.Datetime(required=False)
    schedule_state = fields.Selection(
        selection=_get_schedule_states,
        string="Schedule State",
        readonly=True,
        default="waiting",
        copy=False,
        help="Schedule State used for ordering production",
    )
    schedule_user_id = fields.Many2one(comodel_name="res.users", string="Scheduled by")

    @api.model
    def _set_schedule_states(self):
        """Maybe overrided to add custom state"""
        return [
            ("waiting", _("Waiting")),
            ("todo", _("To-do")),
            ("scheduled", _("Scheduled")),
        ]

    def _get_values_from_selection(self, field):
        res = super()._get_values_from_selection(field)
        if field == "schedule_state":
            res = self._set_schedule_states()
        return res

    def write(self, vals):
        if vals.get("schedule_state") == "scheduled" and not vals.get(
            "date_planned_start"
        ):
            vals["date_planned_start"] = fields.Datetime.now()
            vals["schedule_user_id"] = self.env.user.id
        if vals.get("schedule_state") and vals.get("schedule_state") != "scheduled":
            vals["date_planned_start"] = False
            vals["schedule_user_id"] = False
        return super().write(vals)

    def set_planable_mo(self):
        """Set the MO as to able to be manufactured 'ToDo'
        if it is ready to produce
        """
        for mo in self:
            # If MO has been scheduled when it was not ready yet (still in
            # waiting schedule_state, we can jump to schedule state already)
            if mo.date_planned_start:
                mo.schedule_state = "scheduled"
            else:
                mo.schedule_state = "todo"
        return True

    def action_ready(self):
        res = super().action_ready()
        self.set_planable_mo()
        return res
