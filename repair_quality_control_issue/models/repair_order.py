# Copyright 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    qc_issue_id = fields.Many2one(
        comodel_name="qc.issue",
        string="Quality Control Issue",
    )
