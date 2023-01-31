# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _create_workorder(self):
        res = super()._create_workorder()
        for workorder in self.workorder_ids:
            workorder.ref = workorder.operation_id.ref
        return res
