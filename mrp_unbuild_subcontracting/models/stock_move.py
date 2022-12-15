from collections import defaultdict

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_confirm(self, merge=True, merge_into=False):
        if self.origin_returned_move_id:
            subcontract_details_per_picking = defaultdict(list)
            move_to_not_merge = self.env["stock.move"]
            for move in self:
                if (
                    move.location_dest_id.usage == "supplier"
                    and move.location_id
                    == self.picking_id.picking_type_id.default_location_src_id
                ):
                    continue
                if move.move_orig_ids.production_id:
                    continue
                bom = move._get_subcontract_bom()
                if not bom:
                    continue
                if (
                    float_is_zero(
                        move.product_qty, precision_rounding=move.product_uom.rounding
                    )
                    and move.picking_id.immediate_transfer is True
                ):
                    raise UserError(_("To subcontract, use a planned transfer."))
                subcontract_details_per_picking[move.picking_id].append((move, bom))
                move.write(
                    {
                        "is_subcontract": True,
                    }
                )
                move_to_not_merge |= move
            for picking, subcontract_details in subcontract_details_per_picking.items():
                picking._subcontracted_produce_unbuild(subcontract_details)

            # We avoid merging move due to complication with stock.rule.
            res = super(StockMove, move_to_not_merge)._action_confirm(merge=False)
            res |= super(StockMove, self - move_to_not_merge)._action_confirm(
                merge=merge, merge_into=merge_into
            )
            if subcontract_details_per_picking:
                self.env["stock.picking"].concat(
                    *list(subcontract_details_per_picking.keys())
                ).action_assign()
            return res
        result = super(StockMove, self)._action_confirm(
            merge=merge, merge_into=merge_into
        )
        return result
