# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from tools.translate import _

import logging
_logger = logging.getLogger(__name__)


def id_of(obj):
    """ For o2m relations, returns the foreign id if it is set or None """
    if obj:
        return obj.id
    else:
        return None


def get_target(productions):
    def sort_key(prod):
        return (
            # Prioritize in production and ready
            {"in_production": 1,
             "ready": 2}.get(prod.state, 9),
            # Then the oldest id
            prod.id,
        )

    productions = sorted(productions, key=sort_key)
    return productions[0], productions[1:]


def name_of(obj):
    return getattr(obj, "name", repr(obj))


def moves_mergeable(source, target):
    return all((
        target.state not in ('cancel', 'done'),
        source.product_id.id == target.product_id.id,
        id_of(source.prodlot_id) == id_of(target.prodlot_id),
        id_of(source.product_uom) == id_of(target.product_uom),
        source.location_id.id == target.location_id.id,
        source.location_dest_id.id == target.location_dest_id.id,
    ))


def merge_moves(obj, cr, uid, source_moves, target_moves, updates, to_cancel):
    proc_order_obj = obj.pool.get("procurement.order")
    for to_merge in source_moves:
        for mergeable in target_moves:
            if moves_mergeable(to_merge, mergeable):
                orig_product = to_merge.product_id.id
                orig_uom = id_of(to_merge.product_uom)
                # We found a suitable merge target, do the merge
                while to_merge and mergeable:
                    # Begin updating the move chain until we have a
                    # procurement order on the move
                    to_write = updates.setdefault(
                        mergeable.id,
                        {"product_qty": mergeable.product_qty}
                    )

                    _logger.debug("Merging move %s into move %s (%d %s)",
                                  to_merge.id, mergeable.id,
                                  to_merge.product_qty, to_merge.product_id.name)
                    to_write["product_qty"] += to_merge.product_qty
                    to_cancel.append(to_merge.id)

                    # Get the next in the chain
                    to_merge = to_merge.move_dest_id
                    mergeable = mergeable.move_dest_id
                    if to_merge and mergeable:
                        if not moves_mergeable(to_merge, mergeable):
                            break
                        # Find a procurement order on the moves
                        if proc_order_obj.search(cr, uid, [('move_id', 'in', (to_merge.id, mergeable.id))]):
                            break
                        # Don't allow a change of product or unit
                        if to_merge.product_id.id != orig_product:
                            break
                        if id_of(to_merge.product_uom) != orig_uom:
                            break

                # Found a target, stop searching
                break
        else:
            raise orm.except_orm(
                _("Unable to merge 'To Produce' move"),
                _("No candidate to merge move %s") % (to_merge.id, ),
            )


class mrp_production(orm.Model):
    _inherit = 'mrp.production'

    def _check_productions_mergeable(self, productions):
        if any(production.state in ('done', 'cancel')
               for production in productions):
            raise orm.except_orm(
                _("Invalid Selecetion"),
                _("You cannot merge manufacturing orders that are done"
                  " or cancelled."),
            )

        unique_attrs = (
            ("product_id", _("Product")),
            ("bom_id", _("Bill of Materials")),
            ("product_uom", _("Product UOM")),
            ("location_src_id", _("Source Location")),
            ("location_dest_id", _("Destination Location")),
        )
        for attr, name in unique_attrs:
            values = set(
                id_of(getattr(prod, attr))
                for prod in productions
            )

            if len(values) > 1:
                value_names = ",\n".join([
                    name_of(value)
                    for value in set(getattr(prod, attr) for prod in productions)
                ])
                raise orm.except_orm(
                    _("Incompatible Productions"),
                    _("Unable to merge productions with different %s\n"
                      "Received values:\n%s") % (name, value_names),
                )

    def _do_merge_productions(self, cr, uid, target, productions, context):
        move_obj = self.pool.get("stock.move")
        prod_line_obj = self.pool.get("mrp.production.product.line")

        # Update quantities to produce
        target_write = {
            "product_qty": target.product_qty + sum(
                prod.product_qty for prod in productions,
            ),
        }
        if target.product_uos_qty:
            target_write["product_uos_qty"] = target.product_uos_qty + sum(
                prod.product_uos_qty for prod in productions,
            )

        _logger.debug("Writing to production %d: %r", target.id, target_write)
        target.write(target_write)

        new_picking = {"picking_id": target.picking_id and target.picking_id.id}

        rm_picking_ids = []
        rm_prod_ids = []

        moves_to_produce = [move for move in target.move_created_ids]
        moves_to_consume = [move for move in target.move_lines]
        moves_to_link = []
        moves_to_link2 = []
        prodlines_to_link = []
        moves_to_cancel = []
        move_updates = {}
        # XXX Should we merge notes or add notes of any kind?
        for prod in productions:
            # Merge the pickings
            if prod.picking_id:
                prod.picking_id.write({
                    "move_lines": [(1, mid.id, new_picking)
                                   for mid in prod.picking_id.move_lines],
                })

                rm_picking_ids.append(prod.picking_id.id)

            # Merge the scheduled products
            prodlines_to_link.extend(line.id for line in prod.product_lines)

            # Keep m2m moves to link
            moves_to_link.extend(mid.id for mid in prod.move_lines)
            moves_to_link2.extend(mid.id for mid in prod.move_lines2)

            # Moves "to produce" must be merged with the ones from the target
            # production.
            merge_moves(self, cr, uid,
                        prod.move_created_ids, moves_to_produce,
                        move_updates, moves_to_cancel)
            # Moves "ton consume" should be merged as well
            merge_moves(self, cr, uid,
                        prod.move_lines, moves_to_consume,
                        move_updates, moves_to_cancel)

            # Move all the moves to the new production, cancel the to_produce
            prod.write({
                "move_lines": [(5, )],
                "move_lines2": [(5, )],
            })

            rm_prod_ids.append(prod.id)
            # Done handling one production

        # Update any moves that require updates
        for move_id, write in move_updates.iteritems():
            move_obj.write(cr, uid, [move_id], write, context=context)

        # Update scheduled_products
        prod_line_obj.write(cr, uid, prodlines_to_link, {
            "production_id": target.id,
        })

        # Cancel moves that were merged.
        move_obj.write(cr, uid, moves_to_cancel, {"state": "cancel"})

        target.write({"move_lines": [(4, mid) for mid in moves_to_link],
                      "move_lines2": [(4, mid) for mid in moves_to_link2],
                      })
        prod_obj = self.pool.get("mrp.production")
        picking_obj = self.pool.get("stock.picking")
        # force unlinking of MOs through super calls
        orm.Model.unlink(prod_obj, cr, uid, rm_prod_ids)
        orm.Model.unlink(picking_obj, cr, uid, rm_picking_ids)
        return None

    def action_merge_productions(self, cr, uid, ids, context=None):
        ids = context.pop("active_ids", None)
        if not ids or len(ids) < 2:
            raise orm.except_orm(
                _("Invalid Selection"),
                _("You need to select at least two productions"),
            )

        productions = self.browse(cr, uid, ids)
        self._check_productions_mergeable(productions)
        target, productions = get_target(productions)
        self._do_merge_productions(cr, uid, target, productions, context=context)

        return {
            "name": _("Merged Productions"),
            "view_mode": "form",
            "view_id": False,
            "view_type": "form",
            "res_model": "mrp.production",
            "res_id": target.id,
            "type": 'ir.actions.act_window',
            "domain": '[]',
            "context": context,
        }
