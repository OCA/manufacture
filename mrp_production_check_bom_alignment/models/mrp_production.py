# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import Command, api, fields, models
from odoo.tools import float_compare


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    bom_alignment_warning = fields.Char(
        compute="_compute_bom_alignment_warning",
    )

    @api.depends(
        "state",
        "bom_id",
        "bom_id.bom_line_ids",
        "bom_id.bom_line_ids.product_id",
        "bom_id.bom_line_ids.product_qty",
        "bom_id.bom_line_ids.operation_id",
        "bom_id.byproduct_ids",
        "bom_id.byproduct_ids.product_qty",
        "bom_id.byproduct_ids.operation_id",
        "bom_id.operation_ids",
        "move_raw_ids.bom_line_id",
        "move_raw_ids.product_id",
        "move_raw_ids.state",
        "move_raw_ids.operation_id",
        "move_raw_ids.product_uom_qty",
        "move_finished_ids.byproduct_id",
        "move_finished_ids.state",
        "move_finished_ids.operation_id",
        "move_finished_ids.product_uom_qty",
        "workorder_ids.state",
        "workorder_ids.operation_id",
        "product_qty",
        "product_uom_id",
    )
    def _compute_bom_alignment_warning(self):
        for production in self:
            if production.state in ("done", "cancel"):
                production.bom_alignment_warning = ""
                continue
            production.bom_alignment_warning = (
                production._get_bom_alignment_error(production.name) or ""
            )

    def _get_bom_alignment_error(self, mo_name):
        """Check that the MO's components, by-products, quantities, and operations
        match its BoM.

        Verifies the following things:
        (1) the set of BoM lines covered by raw moves,
        (2) each raw move's ``product_id`` against its BoM line ``product_id``,
        (3) the set of operations covered by work orders,
        (4) each raw move's demand quantity against the BoM line quantity scaled
            to the MO qty,
        (5) each raw move's ``operation_id`` against the current ``operation_id``
            on its BoM line,
        (6) the set of BoM by-products covered by finished moves,
        (7) each by-product move's demand quantity against the BoM by-product quantity
            scaled to the MO qty,
        (8) each by-product move's ``operation_id`` against the current ``operation_id``
            on its BoM by-product.

        Override this method to add or replace alignment checks. Always call
        ``super()`` unless you intend to replace all checks.

        :param str mo_name: display name of the MO, used in error messages.
        :return: translated error message if a misalignment is found, else ``False``.
        :rtype: str | bool
        """
        if not self.bom_id:
            return False
        bom = self.bom_id
        mo_qty_in_bom_uom = self.product_uom_id._compute_quantity(
            self.product_qty, bom.product_uom_id
        )
        factor = mo_qty_in_bom_uom / bom.product_qty if bom.product_qty else 1.0

        # --- Component checks ---
        bom_line_ids = set(bom.bom_line_ids.ids)
        active_moves = self.move_raw_ids.filtered(
            lambda m: m.state != "cancel" and m.bom_line_id
        )
        if bom_line_ids != set(active_moves.bom_line_id.ids):
            products = (
                bom.bom_line_ids.filtered(
                    lambda bl: bl.id not in active_moves.bom_line_id.ids
                ).product_id
                | active_moves.filtered(
                    lambda m: m.bom_line_id.id not in bom_line_ids
                ).product_id
            )
            return self.env._(
                f"The components of MO {mo_name} are not aligned with the current "
                f"BoM configuration: {', '.join(products.mapped('display_name'))}."
            )
        for move in active_moves:
            if move.product_id != move.bom_line_id.product_id:
                return self.env._(
                    f"The components of MO {mo_name} are not aligned with the current "
                    f"BoM configuration."
                )
        for move in active_moves:
            bom_line = move.bom_line_id
            expected_qty = bom_line.product_uom_id._compute_quantity(
                bom_line.product_qty * factor, move.product_uom
            )
            if not self._is_bom_qty_aligned(
                move.product_uom_qty, expected_qty, move.product_uom
            ):
                return self.env._(
                    f"The component quantities of MO {mo_name} are not aligned "
                    f"with the current BoM configuration: "
                    f"{move.product_id.display_name}."
                )
        for move in active_moves:
            if move.operation_id != move.bom_line_id.operation_id:
                return self.env._(
                    f"The 'Consumed in Operation' for components of MO {mo_name} "
                    f"is not aligned with the current BoM configuration: "
                    f"{move.product_id.display_name}."
                )

        # --- Operation checks ---
        bom_operations = bom.operation_ids
        wo_operations = self.workorder_ids.filtered(
            lambda w: w.state != "cancel" and w.operation_id
        ).operation_id
        if set(bom_operations.ids) != set(wo_operations.ids):
            diff_operations = (bom_operations | wo_operations) - (
                bom_operations & wo_operations
            )
            return self.env._(
                f"The operations of MO {mo_name} are not aligned with the current "
                f"BoM configuration: {', '.join(diff_operations.mapped('name'))}."
            )

        # --- By-product checks ---
        active_byproduct_moves = self.move_finished_ids.filtered(
            lambda m: m.state != "cancel" and m.byproduct_id
        )
        if set(bom.byproduct_ids.ids) != set(active_byproduct_moves.byproduct_id.ids):
            products = (
                bom.byproduct_ids.filtered(
                    lambda bp: bp.id not in active_byproduct_moves.byproduct_id.ids
                ).product_id
                | active_byproduct_moves.filtered(
                    lambda m: m.byproduct_id.id not in bom.byproduct_ids.ids
                ).product_id
            )
            return self.env._(
                f"The by-products of MO {mo_name} are not aligned with the current "
                f"BoM configuration: {', '.join(products.mapped('display_name'))}."
            )
        for move in active_byproduct_moves:
            byproduct = move.byproduct_id
            expected_qty = byproduct.product_uom_id._compute_quantity(
                byproduct.product_qty * factor, move.product_uom
            )
            if not self._is_bom_qty_aligned(
                move.product_uom_qty, expected_qty, move.product_uom
            ):
                return self.env._(
                    f"The by-product quantities of MO {mo_name} are not aligned "
                    f"with the current BoM configuration: "
                    f"{move.product_id.display_name}."
                )
        for move in active_byproduct_moves:
            if move.operation_id != move.byproduct_id.operation_id:
                return self.env._(
                    f"The 'Produced in Operation' for by-products of MO {mo_name} "
                    f"is not aligned with the current BoM configuration: "
                    f"{move.product_id.display_name}."
                )

        return False

    def _is_bom_qty_aligned(self, qty, expected_qty, uom):
        # The stored move demand and the recomputed expected qty are rounded
        # through different paths, so tolerate a one-unit rounding difference.
        digits = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        tolerance = max(uom.rounding, 10**-digits)
        return (
            float_compare(
                abs(qty - expected_qty), tolerance, precision_rounding=tolerance
            )
            <= 0
        )

    def action_confirm(self):
        if not self.env.context.get("skip_bom_alignment_check"):
            misaligned = self.filtered(
                lambda mo: mo.state == "draft" and mo._get_bom_alignment_error(mo.name)
            )
            if misaligned:
                wizard = self.env["mrp.bom.alignment.warning"].create(
                    {"mrp_production_ids": [Command.set(self.ids)]}
                )
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "mrp.bom.alignment.warning",
                    "view_mode": "form",
                    "res_id": wizard.id,
                    "target": "new",
                }
        return super().action_confirm()
