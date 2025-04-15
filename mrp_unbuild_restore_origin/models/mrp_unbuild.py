# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    restore_rm_stock_in_origin_loc = fields.Boolean(
        string="Return Components to Original Location",
        help="If selected, components will be returned to the same location"
        " they were taken from during manufacturing.",
    )

    def action_unbuild(self):
        self.ensure_one()
        if self.mo_id:
            self = self.with_context(restore_origin=True)
            if self.restore_rm_stock_in_origin_loc:
                self = self.with_context(exact_location=True)
        return super().action_unbuild()

    def _prepare_move_line_vals(self, move, origin_move_line, taken_quantity):
        vals = super()._prepare_move_line_vals(move, origin_move_line, taken_quantity)
        vals["owner_id"] = origin_move_line.owner_id.id
        if self.env.context.get("exact_location"):
            vals["location_id"] = origin_move_line.location_dest_id.id
            vals["location_dest_id"] = origin_move_line.location_id.id
        return vals

    def _get_move_line_vals(self, move, move_line):
        vals = {
            "move_id": move.id,
            "owner_id": move_line.owner_id.id,
            "qty_done": min(move.product_uom_qty, move_line.qty_done),
            "product_id": move.product_id.id,
            "product_uom_id": move.product_uom.id,
            "location_id": move.location_id.id,
            "location_dest_id": move.location_dest_id.id,
        }
        if self.env.context.get("exact_location"):
            vals["location_id"] = move_line.location_dest_id.id
            vals["location_dest_id"] = move_line.location_id.id
        return vals

    def _generate_produce_moves(self):
        """This logic may seem a bit complex, but it's necessary due to how the following
        standard code works:
        https://github.com/OCA/OCB/blob/52bec03/addons/mrp/models/mrp_unbuild.py#L189-L207
        In short, we need to prepare stock.move.line records in advance with the correct
        values, because the standard logic will otherwise generate them incorrectly
        (e.g., with the wrong destination location or no owner).
        """
        if not self.env.context.get("restore_origin"):
            return super()._generate_produce_moves()
        moves = self.env["stock.move"]
        for unbuild in self:
            raw_moves = unbuild.mo_id.move_raw_ids.filtered(
                lambda move: move.state == "done"
            )
            factor = (
                unbuild.product_qty
                / unbuild.mo_id.product_uom_id._compute_quantity(
                    unbuild.mo_id.product_qty, unbuild.product_uom_id
                )
            )
            for raw_move in raw_moves:
                move = unbuild._generate_move_from_existing_move(
                    raw_move,
                    factor,
                    raw_move.location_dest_id,
                    self.location_dest_id,
                )
                if move.has_tracking == "none":
                    vals_list = []
                    for move_line in raw_move.move_line_ids:
                        vals = self._get_move_line_vals(move, move_line)
                        vals_list.append(vals)
                    self.env["stock.move.line"].create(vals_list)
                    move.write({"state": "confirmed"})
                moves += move
        return moves.with_context(produce_moves=True)
