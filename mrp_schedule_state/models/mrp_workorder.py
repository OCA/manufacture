#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>

from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

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

    def next_schedule_state(self):
        self.ensure_one()
        self.production_id.next_schedule_state()
