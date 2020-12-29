#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>

from odoo import fields, models


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
        related="production_id.date_planned_start",
        string="Schedule MO",
        readonly=True,
        index=True,
        store=True,
    )

    def _iter_selection(self, direction):
        """Allows to update the field selection to its next value
        here, we pass through the related field
        to go towards 'schedule_state' in mrp.production
        """
        for elm in self:
            elm.production_id._iter_selection(direction)
        return True
