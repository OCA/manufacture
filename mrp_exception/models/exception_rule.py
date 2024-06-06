# Copyright (C) 2024, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    production_ids = fields.Many2many(
        comodel_name="mrp.production", string="Production Order"
    )
    model = fields.Selection(
        selection_add=[("mrp.production", "Production Order")],
        ondelete={"mrp.production": "cascade"},
    )
