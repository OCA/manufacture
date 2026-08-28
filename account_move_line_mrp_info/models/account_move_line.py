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

    @api.depends(
        "move_id.stock_move_ids", "move_id.line_ids.mrp_workcenter_productivity_ids"
    )
    def _compute_mrp_production(self):
        for rec in self:
            mrp_production = False
            for stock_move in rec.move_id.stock_move_ids:
                if stock_move.production_id:
                    mrp_production = stock_move.production_id.id
                    break
                elif stock_move.raw_material_production_id:
                    mrp_production = stock_move.raw_material_production_id.id
                    break
            if not mrp_production and rec.move_id.line_ids.mapped(
                "mrp_workcenter_productivity_ids"
            ):
                # Related to labor cost posting
                mrp_production = rec.move_id.line_ids.mapped(
                    "mrp_workcenter_productivity_ids"
                )[0].production_id.id
            rec.mrp_production_id = mrp_production

    @api.depends("move_id.stock_move_ids")
    def _compute_mrp_unbuild(self):
        for rec in self:
            unbuild = False
            for stock_move in rec.move_id.stock_move_ids:
                if stock_move.unbuild_id:
                    unbuild = stock_move.unbuild_id.id
                    break
            rec.unbuild_id = unbuild
