# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    mrp_production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Manufacturing Order",
        compute="_compute_mrp_production",
        store=True,
    )
    unbuild_id = fields.Many2one(
        comodel_name="mrp.unbuild",
        string="Unbuild Order",
        compute="_compute_mrp_unbuild",
        store=True,
    )

    @api.depends("stock_move_id")
    def _compute_mrp_production(self):
        for rec in self:
            if rec.stock_move_id.production_id:
                rec.mrp_production_id = rec.stock_move_id.production_id.id
            elif rec.stock_move_id.raw_material_production_id:
                rec.mrp_production_id = rec.stock_move_id.raw_material_production_id.id
            else:
                rec.mrp_production_id = False

    @api.depends("stock_move_id")
    def _compute_mrp_unbuild(self):
        for rec in self:
            if rec.stock_move_id.unbuild_id:
                rec.unbuild_id = rec.stock_move_id.unbuild_id.id
            else:
                rec.unbuild_id = False
