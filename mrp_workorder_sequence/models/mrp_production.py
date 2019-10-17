# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.multi
    def _reset_work_order_sequence(self):
        for rec in self:
            current_sequence = 1
            for work in rec.workorder_ids:
                work.sequence = current_sequence
                current_sequence += 1

    @api.multi
    def _generate_workorders(self, exploded_boms):
        res = super()._generate_workorders(exploded_boms)
        self._reset_work_order_sequence()
        return res
