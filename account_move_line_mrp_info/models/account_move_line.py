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
    # O2M from the Odoo standard M2O
    mrp_workcenter_productivity_ids = fields.One2many(
        comodel_name="mrp.workcenter.productivity",
        inverse_name="account_move_line_id",
    )

    @api.depends("stock_move_id", "move_id.line_ids.mrp_workcenter_productivity_ids")
    def _compute_mrp_production(self):
        for rec in self:
            if rec.stock_move_id.production_id:
                rec.mrp_production_id = rec.stock_move_id.production_id.id
            elif rec.stock_move_id.raw_material_production_id:
                rec.mrp_production_id = rec.stock_move_id.raw_material_production_id.id
            elif rec.move_id.line_ids.mapped("mrp_workcenter_productivity_ids"):
                # Related to labor cost posting
                rec.mrp_production_id = rec.move_id.line_ids.mapped(
                    "mrp_workcenter_productivity_ids"
                )[0].production_id.id
            else:
                rec.mrp_production_id = False

    @api.depends("stock_move_id")
    def _compute_mrp_unbuild(self):
        for rec in self:
            if rec.stock_move_id.unbuild_id:
                rec.unbuild_id = rec.stock_move_id.unbuild_id.id
            else:
                rec.unbuild_id = False
