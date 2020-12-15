# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WorkCenterAnalyticEstimate(models.Model):
    _inherit = "mrp.workcenter.analytic.estimate"

    work_center_id = fields.Many2one(
        related="work_order_id.workcenter_id",
        string="Work Center",
    )
