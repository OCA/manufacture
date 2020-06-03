# Copyright 2016  Agile Business Group
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    date_repair = fields.Datetime(
        string="Repair Date",
        default=fields.Datetime.now,
        copy=False,
        help="Date of the repair, this field and user_id defines the calendar",
    )
