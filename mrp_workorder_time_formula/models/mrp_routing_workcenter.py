# Copyright 2026 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    time_fixed = fields.Float(
        string="Fixed Duration",
        default=0.0,
        help="Fixed duration in minutes added to the work order duration, "
        "independent of the quantity to produce.",
    )
    time_cadence = fields.Float(
        string="Cadence (units/min)",
        default=0.0,
        help="Production cadence expressed in units produced per minute. "
        "When set, the time per unit is computed as 1 / cadence and added "
        "to the work order duration. Leave at 0 to ignore.",
    )
