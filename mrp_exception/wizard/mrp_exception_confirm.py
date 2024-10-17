# Copyright (C) 2024, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpExceptionConfirm(models.TransientModel):
    _name = "mrp.exception.confirm"
    _description = "MRP exception wizard"
    _inherit = ["exception.rule.confirm"]

    related_model_id = fields.Many2one("mrp.production", "MRP Production")

    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id.ignore_exception = True
            self.related_model_id.action_confirm()
        return super().action_confirm()
