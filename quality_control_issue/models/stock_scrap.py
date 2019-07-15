# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Aleph Objects, Inc. (https://www.alephobjects.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QualityControlIssueStage(models.Model):
    _inherit = "stock.scrap"

    qc_issue_id = fields.Many2one(
        comodel_name="qc.issue", string="Quality Control Issue")
