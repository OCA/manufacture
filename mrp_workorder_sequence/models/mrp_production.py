# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _reset_work_order_sequence(self):
        for rec in self:
            current_sequence = 1
            for work in rec.workorder_ids:
                work.sequence = current_sequence
                current_sequence += 1

    def _create_workorder(self):
        res = super()._create_workorder()
        self._reset_work_order_sequence()
        return res
