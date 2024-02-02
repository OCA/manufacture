# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    blocking_stage = fields.Boolean(default=False, copy=False)
    recommended_blocking_time = fields.Float(copy=False)
