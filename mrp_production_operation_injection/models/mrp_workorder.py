# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class MrpWorkorder(models.Model):

    _inherit = "mrp.workorder"

    sequence = fields.Integer(readonly=True)

    def _action_confirm(self):
        # HACK: Ensure self is ordered according to redefined _order attribute
        #  in mrp_sequence module as _action_confirm needs to loop in this
        #  order to redefine next_work_order_id properly
        self = self.sorted()
        return super()._action_confirm()
