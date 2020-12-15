# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MRPWorkorder(models.Model):
    _inherit = "mrp.workorder"

    duration_estimated = fields.Float(string="Duration (Estimated)", readonly=True)
