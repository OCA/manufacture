# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    qty_planned = fields.Float()

    # Improve the unconsume descrition on SVL and JE
    # (originally "Correction of False (modification of past move)")
    # and add link to the MO Tracking Items
    def _create_in_svl(self, forced_quantity=None):
        res = self.env["stock.valuation.layer"]
        for move in self:
            svl = super(StockMove, move)._create_in_svl(forced_quantity=forced_quantity)
            if move.raw_material_production_id:
                svl.description = "%s - %s (consumption)" % (
                    move.raw_material_production_id.name,
                    move.product_id.name,
                )
                tracking_item = move.analytic_tracking_item_id
                svl.account_move_id.analytic_tracking_item_id = tracking_item

            res |= svl
        return res

    def _create_out_svl(self, forced_quantity=None):
        res = self.env["stock.valuation.layer"]
        for move in self:
            svl = super(StockMove, move)._create_out_svl(
                forced_quantity=forced_quantity
            )
            if move.raw_material_production_id:
                svl.description = "%s - %s (consumption)" % (
                    move.raw_material_production_id.name,
                    move.product_id.name,
                )
                tracking_item = move.analytic_tracking_item_id
                svl.account_move_id.analytic_tracking_item_id = tracking_item
            res |= svl
        return res

    @api.depends(
        "raw_material_production_id.qty_producing", "product_uom_qty", "product_uom"
    )
    def _compute_should_consume_qty(self):
        res = super()._compute_should_consume_qty()
        # Components added after MO confirmation have expected qty zero
        for move in self:
            mo = move.raw_material_production_id
            if mo.id and mo.state != "draft":
                move.should_consume_qty = 0
        return res

    # Store related Tracking Item, for computation efficiency
    analytic_tracking_item_id = fields.Many2one(
        "account.analytic.tracking.item",
        string="Tracking Item",
        copy=True
        # Copy Tracking item, so that when a move is split,
        # it still related to the same Tracking Item
    )

    def _prepare_mrp_raw_material_analytic_line(self):
        values = super()._prepare_mrp_raw_material_analytic_line()
        # Ensure the related Tracking Item is populated
        if not self.analytic_tracking_item_id:
            item_vals = {
                "production_id": values.get("manufacturing_order_id"),
                "product_id": values.get("product_id"),
            }
            item = self.raw_material_production_id._get_matching_tracking_item(
                item_vals
            )
            self.analytic_tracking_item_id = item
        values["analytic_tracking_item_id"] = self.analytic_tracking_item_id.id
        return values

    def generate_mrp_raw_analytic_line(self):
        res = super().generate_mrp_raw_analytic_line()
        # When recording actuals, consider posting WIP immediately
        mos_to_post = self.raw_material_production_id.filtered("is_post_wip_automatic")
        mos_to_post.action_post_inventory_wip()
        return res

    @api.model
    def create(self, vals):
        new_moves = super().create(vals)
        new_moves.raw_material_production_id.populate_ref_bom_tracking_items()
        return new_moves

    def write(self, vals):
        res = super().write(vals)
        self.raw_material_production_id.populate_ref_bom_tracking_items()
        return res
