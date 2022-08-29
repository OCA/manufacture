from odoo import SUPERUSER_ID, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _create_picking(self):
        StockPicking = self.env["stock.picking"]
        for order in self.filtered(lambda po: po.state in ("purchase", "done")):
            non_sub_lines = self.env["stock.move"]
            po = self.env["purchase.order"]
            if any(
                product.type in ["product", "consu"]
                for product in order.order_line.product_id
            ):
                order = order.with_company(order.company_id)
                po = order
                pickings = order.picking_ids.filtered(
                    lambda x: x.state not in ("done", "cancel")
                )
                if not pickings:
                    res = order._prepare_picking()
                    picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                else:
                    picking = pickings[0]
                moves = order.order_line._create_stock_moves(picking)
                moves = moves.filtered(
                    lambda x: x.state not in ("done", "cancel")
                )._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view(
                    "mail.message_origin_link",
                    values={"self": picking, "origin": order},
                    subtype_id=self.env.ref("mail.mt_note").id,
                )
                for move in picking.move_lines:
                    if not move.is_subcontract:
                        non_sub_lines |= move
                        move.picking_id = False
                is_subcontracted_bom = False
                for move in picking.move_ids_without_package:
                    bom = (
                        self.env["mrp.bom"]
                        .sudo()
                        ._bom_find(
                            product=move.product_id,
                            company_id=move.company_id.id,
                            bom_type="subcontract",
                        )
                    )
                    if bom:
                        is_subcontracted_bom = True
                if is_subcontracted_bom:
                    picking.move_ids_without_package.write({"state": "draft"})
                    picking.write({"state": "subcontracted"})
            if non_sub_lines:
                res = po._prepare_picking()
                picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                for move in non_sub_lines:
                    move.write({"picking_id": picking.id})
        return True
