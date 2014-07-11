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

from openerp.osv import orm, fields
from tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class mrp_merge_possibility(orm.TransientModel):
    _name = "mrp.production.merge.choice"
    _description = "Merge Possibility"
    _columns = {
        "production_id": fields.many2one("mrp.production", "Production", readonly=True),
        "merge": fields.boolean("Select"),
        "wizard_id": fields.many2one("mrp.production.merge.wizard", "Wizard", readonly=True)
    }


def id_of(obj):
    """ For o2m relations, returns the foreign id if it is set or None """
    if obj:
        return obj.id
    else:
        return None


def moves_mergeable(source, target):
    return all((
        target.state not in ('cancel', 'done'),
        source.product_id.id == target.product_id.id,
        id_of(source.prodlot_id) == id_of(target.prodlot_id),
        id_of(source.product_uom) == id_of(target.product_uom),
        source.location_id.id == target.location_id.id,
        source.location_dest_id.id == target.location_dest_id.id,
    ))


class mrp_production_merge_wizard(orm.TransientModel):
    _name = "mrp.production.merge.wizard"
    _description = "Merge Productions"
    _columns = {
        "state": fields.selection([
            ("target", "Select Target"),
            ("merge", "Select Merges"),
            ("confirm", "Confirm Merges"),
        ]),
        "target_production_id": fields.many2one("mrp.production", "Target Production"),
        "selected_merge_ids": fields.many2many("mrp.production", "m2m_prod_merge_wizard_sel_ids",
                                               "wizard_id", "production_id", "Selected Productions"),
        "possible_merge_ids": fields.one2many("mrp.production.merge.choice", "wizard_id", "Merge Choices"),
    }

    def _get_merge_choices(self, cr, uid, target_id):
        mrp_obj = self.pool["mrp.production"]
        target = mrp_obj.browse(cr, uid, target_id)
        if not target:
            raise orm.except_orm(
                _("Undefined target"),
                _("No production found with id %d") % (target_id, ),
            )

        production_ids = mrp_obj.search(cr, uid, [
            ('id', '!=', target_id),
            ('state', 'not in', ('cancel', 'done')),
            ('product_id', '=', target.product_id.id),
            ('bom_id', '=', target.bom_id.id),
            ('product_uom', '=', target.product_uom.id),
            ('location_src_id', '=', target.location_src_id.id),
            ('location_dest_id', '=', target.location_dest_id.id),
            ('company_id', '=', target.company_id.id),
        ])

        return production_ids

    def _get_single_target(self, cr, uid, target_id):
        target = self.pool["mrp.production"].browse(cr, uid, target_id)
        if target.state in ('done', 'cancel'):
            raise orm.except_orm(
                _("Not allowed"),
                _("You are not allowed to merge productions in the 'done'"
                  " or 'cancel' states."),
            )
        return {
            "state": "merge",
            "target_production_id": target_id,
            "possible_merge_ids": [
                (0, 0, {"production_id": prod_id,
                        "merge": False})
                for prod_id in self._get_merge_choices(cr, uid, target_id)
            ],
        }

    def default_get(self, cr, uid, fields_list, context=None):
        if context and context.get("active_ids"):
            active_ids = context["active_ids"]
            if len(active_ids) == 1:
                return self._get_single_target(cr, uid, active_ids[0])
            else:
                return {
                    "state": "target",
                    "possible_merge_ids": [
                        (0, 0, {"production_id": prod_id,
                                "merge": False})
                        for prod_id in active_ids
                    ]
                }
        elif context and context.get("active_id"):
            return self._get_single_target(cr, uid, context["active_id"])
        else:
            return {"state": "target"}

    def _refresh(self, id, context):
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': id,
            'views': [(False, 'form')],
            'target': 'new',
            'context': context,
        }

    def do_set_target(self, cr, uid, ids, context=None):
        form = self.browse(cr, uid, ids[0], context=context)
        self.write(cr, uid, ids, {
            "state": "merge",
            "possible_merge_ids": [
                (0, 0, {"production_id": prod_id,
                        "merge": False})
                for prod_id in self._get_merge_choices(
                    cr, uid, form.target_production_id.id)
            ]
        })
        return self._refresh(ids[0], context)

    def do_set_merges(self, cr, uid, ids, context=None):
        form = self.browse(cr, uid, ids[0], context=context)
        self.write(cr, uid, ids, {
            "state": "confirm",
            "selected_merge_ids": [
                (4, merge.production_id.id)
                for merge in form.possible_merge_ids
                if merge.merge
            ]})
        return self._refresh(ids[0], context)

    def do_merge(self, cr, uid, ids, context=None):
        prod_order_obj = self.pool["procurement.order"]
        move_obj = self.pool["stock.move"]

        form = self.browse(cr, uid, ids[0])
        target = form.target_production_id
        target_write = {
            "product_qty": target.product_qty + sum(
                prod.product_qty for prod in form.selected_merge_ids
            ),
        }
        if target.product_uos_qty:
            target_write["product_uos_qty"] = target.product_uos_qty + sum(
                prod.product_uos_qty for prod in form.selected_merge_ids
            )
        _logger.debug("Writing to production %d: %r", target.id, target_write)
        target.write(target_write)

        new_picking = {"picking_id": target.picking_id and target.picking_id.id}

        rm_picking_ids = []
        rm_prod_ids = []

        moves_to_produce = [move for move in target.move_created_ids]
        moves_to_link = []
        moves_to_link2 = []
        moves_to_cancel = []
        move_updates = {}
        # XXX Should we merge notes or add notes of any kind?
        for prod in form.selected_merge_ids:
            # Merge the pickings
            if prod.picking_id:
                prod.picking_id.write({
                    "move_lines": [(1, mid.id, new_picking)
                                   for mid in prod.picking_id.move_lines],
                })

                rm_picking_ids.append(prod.picking_id.id)

            # Keep m2m moves to link
            moves_to_link.extend(mid.id for mid in prod.move_lines)
            moves_to_link2.extend(mid.id for mid in prod.move_lines2)

            # Moves "to produce" must be merged with the ones from the target
            # production.
            for to_merge in prod.move_created_ids:
                for mergeable in moves_to_produce:
                    if moves_mergeable(to_merge, mergeable):
                        orig_product = to_merge.product_id.id
                        orig_uom = id_of(to_merge.product_uom)
                        # We found a suitable merge target, do the merge
                        while to_merge and mergeable:
                            # Begin updating the move chain until we have a
                            # procurement order on the move
                            to_write = move_updates.setdefault(
                                mergeable.id,
                                {"product_qty": mergeable.product_qty}
                            )

                            _logger.debug("Merging move %s into move %s", to_merge.id, mergeable.id)
                            to_write["product_qty"] += to_merge.product_qty
                            moves_to_cancel.append(to_merge.id)

                            # Get the next in the chain
                            to_merge = to_merge.move_dest_id
                            mergeable = mergeable.move_dest_id
                            if to_merge and mergeable:
                                if not moves_mergeable(to_merge, mergeable):
                                    break
                                # Find a procurement order on the moves
                                if prod_order_obj.search(cr, uid, [('move_id', 'in', (to_merge.id, mergeable.id))]):
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

            # Update any moves that require updates
            for move_id, write in move_updates.iteritems():
                move_obj.write(cr, uid, [move_id], write, context=context)

            move_obj.write(cr, uid, moves_to_cancel, {"state": "cancel"})

            # Move all the moves to the new production, cancel the to_produce
            prod.write({
                "move_lines": [(5, )],
                "move_lines2": [(5, )],
            })

            rm_prod_ids.append(prod.id)

        target.write({"move_lines": [(4, mid) for mid in moves_to_link],
                      "move_lines2": [(4, mid) for mid in moves_to_link2],
                      })
        prod_obj = self.pool["mrp.production"]
        picking_obj = self.pool["stock.picking"]
        # force unlinking of MOs through super calls
        orm.Model.unlink(prod_obj, cr, uid, rm_prod_ids, context=context)
        orm.Model.unlink(picking_obj, cr, uid, rm_picking_ids, context=context)
        return None


class mrp_production(orm.Model):
    _inherit = 'mrp.production'

    def action_open_merge_wizard(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('active_model') != self._name:
            context.update(active_ids=ids, active_model=self._name)

        wizard_id = self.pool["mrp.production.merge.wizard"].create(
            cr, uid, {}, context=context)

        return {
            "name": _("Merge Productions"),
            "view_mode": "form",
            "view_id": False,
            "view_type": "form",
            "res_model": "mrp.production.merge.wizard",
            "res_id": wizard_id,
            "type": 'ir.actions.act_window',
            "nodestroy": True,
            "target": "new",
            "domain": '[]',
            "context": context,
        }
