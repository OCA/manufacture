# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _reset_sequence(self):
        for rec in self:
            for sequence, line in enumerate(
                rec.bom_line_ids.sorted(
                    lambda bom_line: (bom_line.sequence, bom_line.id)
                ),
                start=1,
            ):
                if line.sequence != sequence:
                    line.sequence = sequence

    def copy(self, default=None):
        return super(MrpBom, self.with_context(keep_line_sequence=True)).copy(default)
