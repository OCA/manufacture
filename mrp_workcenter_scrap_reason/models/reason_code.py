# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ScrapReasonCode(models.Model):
    _inherit = "scrap.reason.code"

    mrp_workcenter_ids = fields.Many2many(
        string="Allowed Work Centers",
        comodel_name="mrp.workcenter",
        help="Indicate the work centers that can use this reason code "
        "when doing a scrap. If left empy, this reason code can be used "
        "with any work center.",
    )
