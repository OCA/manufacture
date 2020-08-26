#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = ["mrp.production", "selection.rotate.mixin"]
    # _inherit = "mrp.production"
    _name = "mrp.production"

    @api.model
    def _get_schedule_states(self):
        return self._set_schedule_states()

    schedule_state = fields.Selection(
        selection=_get_schedule_states,
        string="Schedule State",
        readonly=True,
        default="waiting",
        help="Schedule State used for ordering production",
    )
    # We don't use native date_planned field because it does not have the
    # same purpose.
    schedule_date = fields.Datetime(
        help="Date at which the manufacture order is scheduled"
    )
    schedule_user_id = fields.Many2one(comodel_name="res.users", string="Scheduled by")

    @api.model
    def _set_schedule_states(self):
        """ Maybe overrided to add custom state
        """
        return [
            ("waiting", _("Waiting")),
            ("todo", _("To-do")),
            ("scheduled", _("Scheduled")),
        ]

    @api.constrains('schedule_state', 'state')
    def _check_planned_state(self):
        productions = self.search(
            [
                ["id", "in", self.ids],
                ["state", "=", "confirmed"],
                ["schedule_state", "!=", "waiting"],
            ]
        )
        if productions:
            production_name = []
            for production in productions:
                production_name.append(production.name)
            raise ValidationError(
                _(
                    "The following production order are not ready and can not "
                    "be scheduled yet : %s"
                )
                % ", ".join(production_name)
            )

    def _get_values_from_selection(self, field):
        res = super()._get_values_from_selection(field)
        if field == "schedule_state":
            # also check model name ?
            res = self._set_schedule_states()
        return res

    def write(self, vals):
        if vals.get("schedule_state") == "scheduled" and not vals.get("schedule_date"):
            vals["schedule_date"] = fields.Datetime.now()
            vals["schedule_user_id"] = self.env.user.id
        if vals.get("schedule_state") and vals.get("schedule_state") != "scheduled":
            vals["schedule_date"] = False
            vals["schedule_user_id"] = False
        return super().write(vals)

    def set_planable_mo(self):
        """ Set the MO as to able to be manufactured 'ToDo'
            if it is ready to produce
        """
        # TODO perf: evaluate self.filtered with schedule_date ???
        for mo in self:
            # If MO has been scheduled when it was not ready yet (still in
            # waiting schedule_state, we can jump to schedule state already)
            if mo.schedule_date:
                mo.schedule_state = "scheduled"
            else:
                mo.schedule_state = "todo"
        return True

    def action_ready(self):
        res = super().action_ready()
        self.set_planable_mo()
        return res


class MrpWorkorder(models.Model):
    _inherit = ["mrp.workorder", "selection.rotate.mixin"]
    _name = "mrp.workorder"

    schedule_state = fields.Selection(
        related="production_id.schedule_state",
        string="MO Schedule",
        index=True,
        store=True,
        readonly=True,
        help="'sub state' of MO state 'Ready To Produce' dedicated to "
        "planification, scheduling and ordering",
    )
    schedule_mo = fields.Datetime(
        related="production_id.schedule_date",
        string="Schedule MO",
        readonly=True,
        index=True,
        store=True,
    )

    def _iter_selection(self, direction):
        """ Allows to update the field selection to its next value
            here, we pass through the related field
            to go towards 'schedule_state' in mrp.production
        """
        for elm in self:
            elm.production_id._iter_selection(direction)
        return True
