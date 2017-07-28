# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class QualityControlIssueStage(models.Model):
    _inherit = "stock.scrap"

    qc_issue_id = fields.Many2one(
        comodel_name="qc.issue", string="Quality Control Issue")
