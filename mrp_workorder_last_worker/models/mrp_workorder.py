# Copyright 2025 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    last_worker_id = fields.Many2one(
        comodel_name="res.users",
        compute="_compute_last_worker_id",
    )

    @api.depends("time_ids.date_start", "time_ids.user_id")
    def _compute_last_worker_id(self):
        for workorder in self:
            workorder.last_worker_id = False
            last_time = workorder.time_ids.sorted(
                key=lambda time: time.date_start, reverse=True
            )
            if last_time:
                workorder.last_worker_id = last_time[0].user_id
