# Copyright 2023 Quartile Limited
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import config, float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        moves_with_no_check = self.filtered(lambda x: x.is_subcontract).with_context(
            skip_negative_qty_check=True
        )
        # For rather unlikely occassions where linked production is not in the right
        # state.
        for move in moves_with_no_check:
            production_moves = self.search(
                [
                    ("move_dest_ids", "=", move.id),
                    ("state", "not in", ("done", "cancel")),
                ]
            )
            productions = production_moves.production_id
            unassigned_productions = productions.filtered(
                lambda p: p.reservation_state != "assigned"
            )
            unassigned_productions.action_assign()
            if all(
                state == "assigned"
                for state in unassigned_productions.mapped("reservation_state")
            ):
                continue
            moves_with_no_check -= move
            # If you have not been able to allocate previously it is because there is
            # no stock, therefore it will leave the stock negative, we deduct the
            # quantity checking the components and show the corresponding error.
            test_condition = (
                config["test_enable"] and self.env.context.get("test_stock_no_negative")
            ) or not config["test_enable"]
            if not test_condition:
                continue
            qty_precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            for p_move in unassigned_productions.move_raw_ids.filtered(
                lambda x: x.state != "assigned"
                and not x.product_id.allow_negative_stock
                and not x.product_id.categ_id.allow_negative_stock
                and not x.location_id.allow_negative_stock
            ):
                product = p_move.product_id.sudo()
                location = p_move.location_id
                location_qty = product.with_context(location=location.id).free_qty
                new_qty = location_qty - p_move.product_uom_qty
                if float_compare(new_qty, 0, precision_digits=qty_precision) == -1:
                    raise ValidationError(
                        _(
                            "You cannot validate this stock operation because the "
                            "stock level of the component product '{name}' would become "
                            "negative ({qty}) on the stock location '{location}' and "
                            "negative stock is not allowed for this product and/or "
                            "location."
                        ).format(
                            name=product.display_name,
                            qty=new_qty,
                            location=location.complete_name,
                        )
                    )
        res = super(StockMove, self - moves_with_no_check)._action_done(
            cancel_backorder=cancel_backorder
        )
        res += super(StockMove, moves_with_no_check)._action_done(
            cancel_backorder=cancel_backorder
        )
        return res
