# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_lot_number_propagated = fields.Boolean(
        default=False,
        readonly=True,
        help=(
            "Lot/serial number is propagated "
            "from a component to the finished product."
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
                    _(
                        "Bill of material is marked for lot number propagation, but "
                        "there are no components propagating lot number. "
                        "Please check BOM configuration."
                    )
                )
            elif len(propagate_move) > 1:
                raise UserError(
                    _(
                        "Bill of material is marked for lot number propagation, but "
                        "there are multiple components propagating lot number. "
                        "Please check BOM configuration."
                    )
                )
            else:
                propagate_move.propagate_lot_number = True

    def _post_inventory(self, cancel_backorder=False):
        self._create_and_assign_propagated_lot_number()
        return super()._post_inventory(cancel_backorder=cancel_backorder)

    def _create_and_assign_propagated_lot_number(self):
        for order in self:
            if not order.is_lot_number_propagated or order.lot_producing_id:
                continue
            finish_moves = order.move_finished_ids.filtered(
                lambda mv, mo=order: mv.product_id == mo.product_id
                and mv.state not in ("done", "cancel")
            )
            if finish_moves and not finish_moves.quantity_done:
                lot_model = self.env["stock.lot"]
                lot = lot_model.search(
                    [
                        ("product_id", "=", order.product_id.id),
                        ("company_id", "=", order.company_id.id),
                        ("name", "=", order.propagated_lot_producing),
                    ],
                    limit=1,
                )
                if lot.quant_ids:
                    raise UserError(
                        _(
                            "Lot/Serial number %s already exists and has been used. "
                            "Unable to propagate it."
                        )
                    )
                if not lot:
                    lot = self.env["stock.lot"].create(
                        {
                            "product_id": order.product_id.id,
                            "company_id": order.company_id.id,
                            "name": order.propagated_lot_producing,
                        }
                    )
                order.with_context(lot_propagation=True).lot_producing_id = lot

    def write(self, vals):
        for order in self:
            if (
                order.is_lot_number_propagated
                and vals.get("lot_producing_id")
                and not self.env.context.get("lot_propagation")
            ):
                raise UserError(
                    _(
                        "Lot/Serial number is propagated from a component, "
                        "you are not allowed to change it."
                    )
                )
        return super().write(vals)

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        # Override to hide the "lot_producing_id" field + "action_generate_serial"
        # button if the MO is configured to propagate a serial number
        arch, view = super()._get_view(view_id, view_type, **options)
        if view.name in self._views_to_adapt():
            arch = self._fields_view_get_adapt_lot_tags_attrs(arch)
        return arch, view

    def _views_to_adapt(self):
        """Return the form view names bound to 'mrp.production' to adapt."""
        return ["mrp.production.form"]

    def _fields_view_get_adapt_lot_tags_attrs(self, arch):
        """Hide elements related to lot if it is automatically propagated."""

        for node in arch.xpath(
            "//label[@for='lot_producing_id']"
            "|//field[@name='lot_producing_id']/.."  # parent <div>
        ):
            attr_invisible = node.attrib.get("invisible", "")
            if not attr_invisible:
                node.attrib["invisible"] = "is_lot_number_propagated"
            else:
                node.attrib["invisible"] = (
                    node.attrib["invisible"] + " or is_lot_number_propagated"
                )
        return arch
