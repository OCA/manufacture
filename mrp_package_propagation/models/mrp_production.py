# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_package_propagated = fields.Boolean(
        default=False,
        readonly=True,
        string="Is package propagated?",
        help="Package is propagated from a component to the finished product.",
    )
    propagated_package_id = fields.Many2one(
        comodel_name="stock.quant.package",
        compute="_compute_propagated_package_id",
        string="Propagated package",
        help=(
            "The BoM used on this manufacturing order is set to propagate "
            "package from one of its components. The value will be "
            "computed once the corresponding component is selected."
        ),
    )

    @api.depends(
        "move_raw_ids.propagate_package",
        "move_raw_ids.move_line_ids.qty_done",
        "move_raw_ids.move_orig_ids.move_line_ids.result_package_id",
    )
    def _compute_propagated_package_id(self):
        for order in self:
            order.propagated_package_id = False
            move_with_package = order.move_raw_ids.filtered(
                lambda o: o.propagate_package
            )
            line_with_package = move_with_package.move_line_ids.filtered(
                lambda l: l.package_id
            )
            if len(line_with_package) == 1:
                order.propagated_package_id = line_with_package.package_id
                continue
            # Support for consumable components: as no quant is created for
            # such products Odoo doesn't copy the destination of the ancestor
            # move (Pre-PICK) to the current move of the component.
            # In such case, get the package to propagate from the ancestor
            # move(s).
            if move_with_package and not line_with_package:
                order.propagated_package_id = fields.first(
                    move_with_package.move_orig_ids.move_line_ids.result_package_id
                )

    @api.onchange("bom_id")
    def _onchange_bom_id_package_propagation(self):
        self.is_package_propagated = self.bom_id.package_propagation

    def action_confirm(self):
        res = super().action_confirm()
        self._check_package_propagation()
        self._set_package_propagation_data_from_bom()
        return res

    def _check_package_propagation(self):
        """Ensure we can propagate the component package from the BoM."""
        for order in self:
            bom = order.bom_id
            if not bom.package_propagation:
                continue
            qty_ok = (
                tools.float_compare(
                    order.product_qty,
                    bom.product_qty,
                    precision_rounding=bom.product_uom_id.rounding,
                )
                == 0
            )
            if not qty_ok or order.product_uom_id != bom.product_uom_id:
                raise UserError(
                    _(
                        "The BoM is propagating a package from one component.\n"
                        "As such, the manufacturing order is forced to produce "
                        "the same quantity than the BoM: %s %s"
                    )
                    % (bom.product_qty, bom.product_uom_id.display_name)
                )

    def _set_package_propagation_data_from_bom(self):
        """Copy information from BoM to the manufacturing order."""
        for order in self:
            order.is_package_propagated = order.bom_id.package_propagation
            for move in order.move_raw_ids:
                move.propagate_package = move.bom_line_id.propagate_package

    def _cal_price(self, consumed_moves):
        # Overridden to propagate the package of the component
        # to the finished product
        # NOTE: this is the only method called in '_post_inventory' between
        # the creation of the stock.move.line record on the finished move,
        # and its validation.
        self._create_and_assign_propagated_package()
        return super()._cal_price(consumed_moves)

    def _create_and_assign_propagated_package(self):
        for order in self:
            if not order.is_package_propagated:
                continue
            finish_moves = order.move_finished_ids.filtered(
                lambda m: m.product_id == order.product_id
                and m.state not in ("done", "cancel")
            )
            if finish_moves.move_line_ids:
                finish_moves.move_line_ids.result_package_id = (
                    order.propagated_package_id
                )
