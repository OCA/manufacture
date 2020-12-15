# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MRPWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    cost_type_ids = fields.One2many(
        "mrp.workcenter.analytic.structure",
        "work_center_id",
        string="Cost Type",
    )
