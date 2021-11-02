# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_compare, float_is_zero


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.multi
    def _adjust_procure_method(self):
        # we call super()._adjust_procure_method first and then come back to
        # check for split_procurement rules on the move.
        super()._adjust_procure_method()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for move in self.move_raw_ids:
            product = move.product_id
            routes = (
                product.route_ids +
                product.route_from_categ_ids +
                move.warehouse_id.route_ids
            )
            # find if we have a "split_procurement" rule in the routes
            split_rule = self.env["stock.rule"].search(
                [
                    ("route_id", "in", [x.id for x in routes]),
                    ("location_src_id", "=", move.location_id.id),
                    ("location_id", "=", move.location_dest_id.id),
                    ("action", "=", "split_procurement")
                ],
                limit=1
            )
            if split_rule:
                product_qty = move.product_uom_qty
                uom = move.product_id.uom_id
                needed_qty = split_rule.get_mto_qty_to_order(
                    move.product_id, product_qty, uom, values=None
                )
                if float_is_zero(needed_qty, precision_digits=precision):
                    # no additional product -> MTS
                    move.procure_method = split_rule.mts_rule_id.procure_method
                elif float_compare(needed_qty, product_qty,
                                   precision_digits=precision) == 0.0:
                    # no stock -> MTO
                    move.procure_method = split_rule.mto_rule_id.procure_method
                else:
                    # partial MTS, remainder MTO
                    mts_qty = product_qty - needed_qty
                    mts_rule = split_rule.mts_rule_id
                    mto_rule = split_rule.mto_rule_id
                    move.update(
                        {
                            "procure_method": mts_rule.procure_method,
                            "product_uom_qty": mts_qty
                        }
                    )
                    # create the MTO move, attached to same MO
                    move.copy(
                        default={
                            "procure_method": mto_rule.procure_method,
                            "product_uom_qty": needed_qty
                        }
                    )
