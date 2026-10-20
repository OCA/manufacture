# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, fields, models, tools
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_lot_number_propagated = fields.Boolean(
        default=False,
        readonly=True,
        help=(
            "Lot/serial number is propagated from a component to the finished product."
        ),
    )
    propagated_lot_producing = fields.Char(
        compute="_compute_propagated_lot_producing",
        help=(
            "The BoM used on this manufacturing order is set to propagate "
            "lot number from one of its components. The value will be "
            "computed once the corresponding component is selected."
        ),
    )

    @api.depends(
        "move_raw_ids.propagate_lot_number",
        "move_raw_ids.move_line_ids.quantity",
        "move_raw_ids.move_line_ids.picked",
        "move_raw_ids.move_line_ids.lot_id",
    )
    def _compute_propagated_lot_producing(self):
        for order in self:
            order.propagated_lot_producing = False
            move_with_lot = order._get_propagating_component_move()
            line_with_sn = move_with_lot.move_line_ids.filtered(
                lambda ln: (
                    ln.lot_id
                    and ln.product_id.tracking == "serial"
                    and tools.float_compare(
                        ln.quantity, 1, precision_rounding=ln.product_uom_id.rounding
                    )
                    == 0
                )
            )
            if len(line_with_sn) == 1:
                order.propagated_lot_producing = line_with_sn.lot_id.name

    @api.onchange("bom_id")
    def _onchange_bom_id_lot_number_propagation(self):
        self.is_lot_number_propagated = self.bom_id.lot_number_propagation

    def action_confirm(self):
        res = super().action_confirm()
        self._set_lot_number_propagation_data_from_bom()
        return res

    def _get_propagating_component_move(self):
        self.ensure_one()
        return self.move_raw_ids.filtered(lambda o: o.propagate_lot_number)

    def _get_propagated_lot_names(self):
        """Get serial names reserved on the propagating component.

        Those names are the ones expected on the finished product.
        Only serial-tracked lines holding exactly one unit are usable,
        as the propagation is a 1:1 match between component and finished
        product serials.
        """
        self.ensure_one()
        move = self._get_propagating_component_move()
        lines = move.move_line_ids.filtered(
            lambda ln: (
                ln.lot_id
                and ln.product_id.tracking == "serial"
                and tools.float_compare(
                    ln.quantity, 1, precision_rounding=ln.product_uom_id.rounding
                )
                == 0
            )
        )
        return list(dict.fromkeys(lines.mapped("lot_id.name")))

    def _set_lot_number_propagation_data_from_bom(self):
        """Copy information from BoM to the manufacturing order."""
        for order in self:
            propagate_lot = order.bom_id.lot_number_propagation
            if not propagate_lot:
                continue
            order.is_lot_number_propagated = propagate_lot
            propagate_move = order.move_raw_ids.filtered(
                lambda m: m.bom_line_id.propagate_lot_number
            )
            if not propagate_move:
                raise UserError(
                    self.env._(
                        "Bill of material is marked for lot number propagation, but "
                        "there are no components propagating lot number. "
                        "Please check BOM configuration."
                    )
                )
            elif len(propagate_move) > 1:
                raise UserError(
                    self.env._(
                        "Bill of material is marked for lot number propagation, but "
                        "there are multiple components propagating lot number. "
                        "Please check BOM configuration."
                    )
                )
            else:
                propagate_move.propagate_lot_number = True

    def pre_button_mark_done(self):
        # Pre-assign the finished serials from the reserved components serials.
        # So serials are not generated
        self._create_and_assign_propagated_lot_number()
        return super().pre_button_mark_done()

    def _create_and_assign_propagated_lot_number(self):
        for order in self:
            if not order.is_lot_number_propagated:
                continue
            if order.product_uom_qty > 1:
                # Producing several units, we cannot pre-assign the propagated
                # serials without knowing the quantities produced.
                # So let the wizard check that the entered serials match
                # the reserved component serials.
                continue
            lot_names = order._get_propagated_lot_names()
            if not lot_names:
                # No serial reserved on the propagating component yet
                continue
            if sorted(order.lot_producing_ids.mapped("name")) == sorted(lot_names):
                continue
            finish_moves = order.move_finished_ids.filtered(
                lambda mv, mo=order: mv.product_id == mo.product_id
                and mv.state not in ("done", "cancel")
            )
            if finish_moves and finish_moves.quantity and not finish_moves.picked:
                lots = order._create_or_get_propagated_lots(lot_names)
                order.with_context(lot_propagation=True).lot_producing_ids = lots

    def _create_or_get_propagated_lots(self, lot_names):
        """Find or create the finished product lots matching ``lot_names``."""
        self.ensure_one()
        lots = self.env["stock.lot"]
        for name in lot_names:
            lot = self.env["stock.lot"].search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("company_id", "=", self.company_id.id),
                    ("name", "=", name),
                ],
                limit=1,
            )
            if lot.quant_ids:
                raise UserError(
                    self.env._(
                        "Lot/Serial number %s already exists and has been used. "
                        "Unable to propagate it.",
                        name,
                    )
                )
            if not lot:
                lot = self.env["stock.lot"].create(
                    {
                        "product_id": self.product_id.id,
                        "company_id": self.company_id.id,
                        "name": name,
                    }
                )
            lots |= lot
        return lots

    def write(self, vals):
        for order in self:
            if (
                order.is_lot_number_propagated
                and vals.get("lot_producing_ids")
                and not self.env.context.get("lot_propagation")
            ):
                raise UserError(
                    self.env._(
                        "Lot/Serial number is propagated from a component, "
                        "you are not allowed to change it."
                    )
                )
        return super().write(vals)
