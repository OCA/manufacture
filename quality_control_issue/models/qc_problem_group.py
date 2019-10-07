# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Aleph Objects, Inc. (https://www.alephobjects.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcProblemGroup(models.Model):
    _name = "qc.problem.group"
    _description = "Quality Control Problem Tracking Groups"

    name = fields.Char()
    problem_ids = fields.One2many(
        comodel_name="qc.problem", inverse_name="problem_group_id")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
