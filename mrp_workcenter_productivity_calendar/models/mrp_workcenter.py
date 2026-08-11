# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    use_calendar_for_duration = fields.Boolean(
        string="Use Calendar for Time Tracking Duration",
        help="Compute productive/performance time from the work center's "
        "resource calendar instead of the raw elapsed time, deducting "
        "breaks such as lunch. Requires a resource calendar.",
    )
