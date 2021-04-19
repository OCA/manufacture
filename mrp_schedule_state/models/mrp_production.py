#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>

from odoo import _, api, exceptions, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def _get_schedule_states(self):
        return [
            ("waiting", _("Waiting")),
            ("todo", _("To-do")),
            ("scheduled", _("Scheduled")),
        ]

    # date_planned_start exists but we need it to be empty, until the MO is scheduled
    # We don't want a default date_planned_start, but as the field is required
    # some logic expects it to be always filled, it is hard change this.
    # so we make a new field, hide date_planned_start from view, but synchronize it
    # to our new field to keep standard behaviors based on date_planned_start
    schedule_date = fields.Datetime()
    schedule_state = fields.Selection(
        selection=_get_schedule_states,
        string="Schedule State",
        readonly=False,
        default="waiting",
        copy=False,
        compute="_compute_schedule_state",
        store=True,
        help="Schedule State used for ordering production",
    )
    schedule_user_id = fields.Many2one(comodel_name="res.users", string="Scheduled by")

    def _get_mo_plannable(self):
        res = {}
        for mo in self:
            res[mo.id] = mo.reservation_state == "assigned" and True or False
        return res

    # Schedule state should automatically compute for waiting/todo schedule state.
    # it has to be put on scheduled manually by a user. Once it is scheduled it is
    # unscheduled manually for now.
    @api.depends("reservation_state", "state")
    def _compute_schedule_state(self):
        # A MO is considered plannable when its raw materials are available.
        # but it could be overriden to implement more complexes cases
        plannable_mos = self._get_mo_plannable()
        for mo in self:
            is_plannable = plannable_mos.get(mo.id)
            if mo.state in ("progress", "to_close", "done"):
                mo.schedule_state = "scheduled"
            # already planned
            elif is_plannable and mo.schedule_date:
                mo.schedule_state = "scheduled"
            elif is_plannable:
                mo.schedule_state = "todo"
            else:
                mo.schedule_state = "waiting"

    def write(self, vals):
        # it mean the schedule state is changed manually, not computed
        if vals.get("schedule_state"):
            # scheduling
            if vals["schedule_state"] == "scheduled":
                vals["schedule_user_id"] = self.env.user.id
                if "schedule_date" not in vals:
                    vals["schedule_date"] = fields.Datetime.now()
            # manual unschedule
            else:
                vals["schedule_date"] = False
                vals["schedule_user_id"] = False
        # synchronize schedule date and date_planned_start, which have the same meaning
        # once the MO is scheduled
        if vals.get("schedule_date"):
            vals["date_planned_start"] = vals["schedule_date"]
        return super().write(vals)

    def next_schedule_state(self):
        # schedule state shoudl manually go from todo to scheduled or the contrary
        # but we should not be able to put it manually to waiting, it should be a
        # computed only state
        self.ensure_one()
        if self.schedule_state == "waiting":
            raise exceptions.UserError(_("The MO %s can't be scheduled yet"))
        new_state = self.schedule_state == "scheduled" and "todo" or "scheduled"
        self.schedule_state = new_state
        return True
