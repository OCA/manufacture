# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpBomAlignmentWarning(models.TransientModel):
    _name = "mrp.bom.alignment.warning"
    _description = "BoM Alignment Warning"

    mrp_production_ids = fields.Many2many("mrp.production")
    mrp_production_count = fields.Integer(compute="_compute_mrp_production_count")
    mrp_production_names = fields.Char(compute="_compute_mrp_production_count")

    @api.depends("mrp_production_ids")
    def _compute_mrp_production_count(self):
        for wizard in self:
            wizard.mrp_production_count = len(wizard.mrp_production_ids)
            wizard.mrp_production_names = ", ".join(
                wizard.mrp_production_ids.mapped("name")
            )

    def action_confirm_anyway(self):
        return self.mrp_production_ids.with_context(
            skip_bom_alignment_check=True
        ).action_confirm()

    def action_update_and_confirm(self):
        self.mrp_production_ids.action_update_bom()
        return self.mrp_production_ids.with_context(
            skip_bom_alignment_check=True
        ).action_confirm()
