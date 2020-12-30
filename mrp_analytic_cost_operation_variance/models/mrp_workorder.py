# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MRPWorkorder(models.Model):
    _inherit = "mrp.workorder"

    duration_estimated = fields.Float(string="Duration (Estimated)", readonly=True)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        for order in self.workorder_ids:
            order.duration_estimated = order.duration_expected
        return res
