# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from lxml import etree

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.models.ir_ui_view import (
    transfer_modifiers_to_node,
    transfer_node_to_modifiers,
)


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
        "move_raw_ids.move_line_ids.qty_done",
        "move_raw_ids.move_line_ids.lot_id",
    )
    def _compute_propagated_lot_producing(self):
        for order in self:
            order.propagated_lot_producing = False
            move_with_lot = order._get_propagating_component_move()
            line_with_sn = move_with_lot.move_line_ids.filtered(
                lambda l: (
                    l.lot_id
                    and l.product_id.tracking == "serial"
                    and tools.float_compare(
                        l.qty_done, 1, precision_rounding=l.product_uom_id.rounding
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
                lambda m: m.product_id == order.product_id
                and m.state not in ("done", "cancel")
            )
            if finish_moves and not finish_moves.quantity_done:
                lot_model = self.env["stock.production.lot"]
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
                    lot = self.env["stock.production.lot"].create(
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
                and "lot_producing_id" in vals
                and not self.env.context.get("lot_propagation")
            ):
                raise UserError(
                    _(
                        "Lot/Serial number is propagated from a component, "
                        "you are not allowed to change it."
                    )
                )
        return super().write(vals)

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        # Override to hide the "lot_producing_id" field + "action_generate_serial"
        # button if the MO is configured to propagate a serial number
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if result.get("name") in self._views_to_adapt():
            result["arch"] = self._fields_view_get_adapt_lot_tags_attrs(result)
        return result

    def _views_to_adapt(self):
        """Return the form view names bound to 'mrp.production' to adapt."""
        return ["mrp.production.form"]

    def _fields_view_get_adapt_lot_tags_attrs(self, view):
        """Hide elements related to lot if it is automatically propagated."""
        doc = etree.XML(view["arch"])
        tags = (
            "//label[@for='lot_producing_id']",
            "//field[@name='lot_producing_id']/..",  # parent <div>
        )
        for xpath_expr in tags:
            attrs_key = "invisible"
            nodes = doc.xpath(xpath_expr)
            for field in nodes:
                attrs = safe_eval(field.attrib.get("attrs", "{}"))
                if not attrs[attrs_key]:
                    continue
                invisible_domain = expression.OR(
                    [attrs[attrs_key], [("is_lot_number_propagated", "=", True)]]
                )
                attrs[attrs_key] = invisible_domain
                field.set("attrs", str(attrs))
                modifiers = {}
                transfer_node_to_modifiers(field, modifiers, self.env.context)
                transfer_modifiers_to_node(modifiers, field)
        return etree.tostring(doc, encoding="unicode")
