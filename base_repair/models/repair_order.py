# Copyright 2021 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RepairOrder(models.Model):

    _inherit = "repair.order"

    date_repair = fields.Datetime(
        "Repair Date",
        default=fields.Datetime.now,
        copy=False,
        help="Date of the repair, this field " "and user_id defines the calendar",
    )

    duration = fields.Float("Repair Duration", help="Duration in hours and minutes.")
