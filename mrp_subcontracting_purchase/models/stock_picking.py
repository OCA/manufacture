from datetime import timedelta

from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    subcontracting_source_purchase_count = fields.Integer(
        "Number of subcontracting PO Source",
        compute="_compute_subcontracting_source_purchase_count",
        help="Number of subcontracting Purchase Order Source",
    )

    @api.depends("move_lines.move_dest_ids.raw_material_production_id")
    def _compute_subcontracting_source_purchase_count(self):
        """Compute number of subcontracting Purchase Order Source"""
        for picking in self:
            picking.subcontracting_source_purchase_count = len(
                picking._get_subcontracting_source_purchase()
            )

    def action_view_subcontracting_source_purchase(self):
        """Returns action for subcontracting source purchase"""
        purchase_order_ids = self._get_subcontracting_source_purchase().ids
        action = {
            "res_model": "purchase.order",
            "type": "ir.actions.act_window",
        }
        if len(purchase_order_ids) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": purchase_order_ids[0],
                }
            )
        else:
            action.update(
                {
                    "name": _("Source PO of %s") % self.name,
                    "domain": [("id", "in", purchase_order_ids)],
                    "view_mode": "tree,form",
                }
            )
        return action

    def _get_subcontracting_source_purchase(self):
        """Returns the source purchase order associated with a subcontracted operation."""
        moves_subcontracted = self.move_lines.move_dest_ids.raw_material_production_id.move_finished_ids.move_dest_ids.filtered(  # noqa
            lambda m: m.is_subcontract
        )
        return moves_subcontracted.purchase_line_id.order_id

    def _get_subcontract_production(self):
        """Returns subcontract production in stock picking line"""
        return self.move_lines._get_subcontract_production()

    def _action_done(self):
        # parent function with a subcontract record line added
        res = super(StockPicking, self)._action_done()

        for move in self.move_lines.filtered(lambda move: move.is_subcontract):
            # Auto set qty_producing/lot_producing_id of MO if there isn't tracked component
            # If there is tracked component,
            # the flow use subcontracting_record_component instead
            if move._has_tracked_subcontract_components():
                continue
            production = move.move_orig_ids.production_id.filtered(
                lambda p: p.state not in ("done", "cancel")
            )[-1:]
            if not production:
                continue
            # Manage additional quantities
            quantity_done_move = move.product_uom._compute_quantity(
                move.quantity_done, production.product_uom_id
            )
            if (
                float_compare(
                    production.product_qty,
                    quantity_done_move,
                    precision_rounding=production.product_uom_id.rounding,
                )
                == -1
            ):
                change_qty = self.env["change.production.qty"].create(
                    {"mo_id": production.id, "product_qty": quantity_done_move}
                )
                change_qty.with_context(skip_activity=True).change_prod_qty()
            # Create backorder MO for each move lines
            for move_line in move.move_line_ids:
                if move_line.lot_id:
                    production.lot_producing_id = move_line.lot_id
                production.qty_producing = move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, production.product_uom_id
                )
                production._set_qty_producing()
                production.subcontracting_has_been_recorded = True
                if move_line != move.move_line_ids[-1]:
                    backorder = production._generate_backorder_productions(
                        close_mo=False
                    )
                    # The move_dest_ids won't be set because the _split filter out done move
                    backorder.move_finished_ids.filtered(
                        lambda mo: mo.product_id == move.product_id
                    ).move_dest_ids = production.move_finished_ids.filtered(
                        lambda mo: mo.product_id == move.product_id
                    ).move_dest_ids
                    production.product_qty = production.qty_producing
                    production = backorder

        for picking in self:
            productions_to_done = (
                picking._get_subcontracted_productions()._subcontracting_filter_to_done()
            )
            if not productions_to_done:
                continue
            production_ids_backorder = []
            if not self.env.context.get("cancel_backorder"):
                production_ids_backorder = productions_to_done.filtered(
                    lambda mo: mo.state == "progress"
                ).ids
            productions_to_done.with_context(
                subcontract_move_id=True, mo_ids_to_backorder=production_ids_backorder
            ).button_mark_done()
            # For concistency, set the date on production move before the date
            # on picking. (Traceability report + Product Moves menu item)
            minimum_date = min(picking.move_line_ids.mapped("date"))
            production_moves = (
                productions_to_done.move_raw_ids | productions_to_done.move_finished_ids
            )
            production_moves.write({"date": minimum_date - timedelta(seconds=1)})
            production_moves.move_line_ids.write(
                {"date": minimum_date - timedelta(seconds=1)}
            )
        return res
