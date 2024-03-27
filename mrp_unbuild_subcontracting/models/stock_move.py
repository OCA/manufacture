from collections import defaultdict

from odoo import _, api, models
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
                # CHECK ME: Partial receipt of subcontracting process
                # and refund change move_orig_ids adding all
                # subcontracting origin moves, because
                # that we try to restore and keep consistent data structure
                # https://github.com/odoo/odoo/blob/b57c1332251b1553f98b9ad16b45a47d4101ffb2/addons/stock/wizard/stock_picking_return.py#L151-L153  # noqa: B950
                if (
                    len(move.mapped("move_orig_ids.move_orig_ids.production_id")) > 1
                    and move.origin_returned_move_id
                    and move.origin_returned_move_id.id in move.move_orig_ids.ids
                ):
                    move.write(
                        {"move_orig_ids": [(6, 0, move.origin_returned_move_id.ids)]}
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

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get("move_dest_ids", False) and val.get("production_id", False):
                if (
                    self.env["mrp.production"]
                    .browse(val.get("production_id", False))
                    .bom_id.type
                    == "subcontract"
                ):
                    # When we have partial receive move_orig_ids
                    # keep first subcontracting manufacturing order moves link
                    # should be avoided this situation, to refund cases
                    self.browse(val.get("move_dest_ids", False)[0][1]).write(
                        {
                            "move_orig_ids": [(5, 0, 0)],
                        }
                    )
        return super().create(vals_list)
