# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    sequence = fields.Integer(default=9999, string="original sequence")
    sequence2 = fields.Integer(
        help="Shows the sequence in the BOM line.",
        string="Sequence",
        related="sequence",
        readonly=False,
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        if not self.env.context.get("keep_line_sequence"):
            lines.bom_id._reset_sequence()
        return lines
