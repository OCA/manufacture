# Copyright 2025 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    force_lot_uniqueness = fields.Boolean(
        related="picking_type_id.force_production_lot_uniqueness"
    )

    allowed_lot_producing_ids = fields.Many2many(
        "stock.lot",
        string="Allowed Lot/Serial Numbers",
        compute="_compute_allowed_lot_producing_ids",
    )

    def _compute_allowed_lot_producing_ids(self):
        for record in self:
            lot_ids = self.env["stock.lot"].search(
                [
                    ("product_id", "=", record.product_id.id),
                    ("company_id", "=", record.company_id.id),
                ]
            )
            if record.force_lot_uniqueness and record.product_id.tracking == "lot":
                allowed_lots = lot_ids.filtered(
                    lambda lot: not record._is_finished_lot_already_produced(lot)
                )
                record.allowed_lot_producing_ids = allowed_lots
            else:
                record.allowed_lot_producing_ids = lot_ids

    def _button_mark_done_sanity_checks(self):
        res = super()._button_mark_done_sanity_checks()
        for order in self:
            order._check_lot_uniqueness()
        return res

    def _check_lot_uniqueness(self):
        """Alert the user if the lot number has already been produced.
        This method is based on the odoo code for serial numbers in _check_sn_uniqueness
        """
        if not self.force_lot_uniqueness or not self.lot_producing_id:
            return

        if (
            self.product_tracking == "lot"
            and self.lot_producing_id
            and self._is_finished_lot_already_produced(self.lot_producing_id)
        ):
            raise UserError(
                _(
                    "This lot number for product %s has already been produced",
                    self.product_id.name,
                )
            )

        for move in self.move_finished_ids:
            if move.has_tracking != "lot" or move.product_id == self.product_id:
                continue
            for move_line in move.move_line_ids:
                if self._is_finished_lot_already_produced(
                    move_line.lot_id, excluded_sml=move_line
                ):
                    raise UserError(
                        _(
                            "The lot number %(number)s used for byproduct %(product_name)s"
                            " has already been produced",
                            number=move_line.lot_id.name,
                            product_name=move_line.product_id.name,
                        )
                    )

    def _is_finished_lot_already_produced(self, lot, excluded_sml=None):
        """
        Check if the given lot has already been produced in another MO,
        taking into account unbuilt and scrapped moves, and excluding
        the current production move lines if provided.

        This method is based on the odoo code for serial numbers in
        _is_finished_sn_already_produced
        """
        excluded_move_lines = excluded_sml or self.env["stock.move.line"]

        # Domain for all done move lines with this lot
        base_domain = [("lot_id", "=", lot.id), ("state", "=", "done")]

        # Finished move lines in production location that are not unbuilt
        done_count = self.env["stock.move.line"].search_count(
            base_domain
            + [
                ("location_id.usage", "=", "production"),
                ("move_id.unbuild_id", "=", False),
            ]
        )

        if done_count:
            # Move lines that were unbuilt
            unbuilt_count = self.env["stock.move.line"].search_count(
                base_domain
                + [
                    ("production_id", "=", False),
                    ("location_dest_id.usage", "=", "production"),
                    ("move_id.unbuild_id", "!=", False),
                ]
            )

            # Move lines moved to scrap
            moved_to_scrap_count = self.env["stock.move.line"].search_count(
                base_domain
                + [
                    ("location_id.scrap_location", "=", False),
                    ("location_dest_id.scrap_location", "=", True),
                ]
            )

            # Move lines restored from scrap
            restored_from_scrap_count = self.env["stock.move.line"].search_count(
                [
                    ("lot_id", "=", lot.id),
                    ("state", "=", "done"),
                    ("location_id.scrap_location", "=", True),
                    ("location_dest_id.scrap_location", "=", False),
                ]
            )

            # If any production still exists that was not unbuilt/scrapped, return True
            if not (
                (unbuilt_count or moved_to_scrap_count)
                and done_count
                - unbuilt_count
                - moved_to_scrap_count
                + restored_from_scrap_count
                == 0
            ):
                return True

        # Check duplicates in current production, excluding specified move lines if any
        current_move_lines = self.move_finished_ids.move_line_ids - excluded_move_lines
        duplicates_in_current = current_move_lines.filtered(
            lambda ml: ml.qty_done and ml.lot_id == lot
        )

        return bool(duplicates_in_current)
