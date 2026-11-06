# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models
from odoo.tools import groupby

SKIP_CTX_KEY = "skip_push_mto_qty"


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _push_mto_qty_finished_moves(self):
        return self.move_finished_ids.filtered(
            lambda m: m.product_id == m.production_id.product_id
        )

    def _push_mto_qty_snapshot(self):
        """Store, per production group, the quantity planned on the productions
        of `self`, the productions existing in the group and the destination
        moves of their finished moves.

        The destination moves must be read before the productions are done:
        a push rule (e.g. manufacture in 3 steps) inserts a new move, holding
        the produced quantity, between the finished move and its destinations.
        """
        snapshot = {}
        productions = self.filtered(
            lambda p: p.state not in ("done", "cancel")
            and p.picking_type_id.push_mto_qty_to_dest_moves
        )
        for key, prods in groupby(
            productions, key=lambda p: p.production_group_id.id or f"mo-{p.id}"
        ):
            prods = self.browse(p.id for p in prods)
            uom = prods[0].product_uom_id
            snapshot[key] = {
                "group": prods.production_group_id,
                "uom": uom,
                "productions_before": prods.production_group_id.production_ids | prods,
                "dest_moves": prods._push_mto_qty_finished_moves().move_dest_ids,
                "planned": {
                    p.id: p.product_uom_id._compute_quantity(
                        p.product_qty, uom, round=False
                    )
                    for p in prods
                },
            }
        return snapshot

    def button_mark_done(self):
        # button_mark_done can call itself (e.g. when a backorder is always
        # created): only the outermost call pushes the quantities.
        if self.env.context.get(SKIP_CTX_KEY):
            return super().button_mark_done()
        snapshot = self._push_mto_qty_snapshot()
        res = super(
            MrpProduction, self.with_context(**{SKIP_CTX_KEY: True})
        ).button_mark_done()
        if isinstance(res, dict) and isinstance(res.get("context"), dict):
            # The returned action (e.g. the backorder wizard) copies the
            # context: drop the key so that its own call to button_mark_done
            # pushes the quantities.
            res["context"] = {
                k: v for k, v in res["context"].items() if k != SKIP_CTX_KEY
            }
        self._push_mto_qty_after_mark_done(snapshot)
        return res

    def _push_mto_qty_after_mark_done(self, snapshot):
        """Push to the ensuing moves the difference between the quantity
        planned on the productions done and the quantity produced plus the
        quantity of the backorders created."""
        for data in snapshot.values():
            uom = data["uom"]
            done_productions = self.browse(data["planned"].keys()).filtered(
                lambda p: p.state == "done"
            )
            if not done_productions:
                continue
            finished_moves = done_productions._push_mto_qty_finished_moves()
            produced = sum(
                move.product_uom._compute_quantity(move.quantity, uom, round=False)
                for move in finished_moves.filtered(lambda m: m.state == "done")
            )
            new_backorders = (
                data["group"].production_ids - data["productions_before"]
            ).filtered(lambda p: p.state != "cancel")
            backordered = sum(
                bo.product_uom_id._compute_quantity(bo.product_qty, uom, round=False)
                for bo in new_backorders
            )
            planned = sum(data["planned"][p.id] for p in done_productions)
            delta = produced + backordered - planned
            if uom.compare(delta, 0):
                data["dest_moves"]._push_mto_qty(delta, uom)

    def _action_cancel(self):
        to_push = []
        for production in self.filtered(
            lambda p: p.state not in ("done", "cancel")
            and p.picking_type_id.push_mto_qty_to_dest_moves
        ):
            siblings = production.production_group_id.production_ids - self
            if not siblings.filtered(lambda p: p.state != "cancel"):
                # Standard cancellation (propagate_cancel or MTS fallback)
                continue
            remaining = production.product_qty - production.qty_produced
            if production.product_uom_id.compare(remaining, 0) <= 0:
                continue
            # Read destination moves before the cancellation as the link is
            # removed when the finished move is cancelled
            dest_moves = production._push_mto_qty_finished_moves().move_dest_ids
            if dest_moves:
                to_push.append((dest_moves, -remaining, production.product_uom_id))
        res = super()._action_cancel()
        for dest_moves, qty, uom in to_push:
            dest_moves._push_mto_qty(qty, uom)
        return res
