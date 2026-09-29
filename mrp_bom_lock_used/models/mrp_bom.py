# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, models
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _check_active_production_orders(self):
        """Check for active production orders and raise error if found."""
        production_orders = self.env["mrp.production"].search(
            [("bom_id", "in", self.ids), ("state", "not in", ["done", "cancel"])],
        )

        if production_orders:
            production_names = ", ".join(production_orders.mapped("name"))
            raise UserError(
                _(
                    "Cannot modify BOM lines. "
                    "There are active production orders: %s. "
                    "Please complete or cancel these production orders "
                    "before modifying the BOM."
                )
                % production_names
            )

    def write(self, values):
        # Check if BOM lines are being modified
        if "bom_line_ids" in values:
            self._check_active_production_orders()
        return super().write(values)


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    def write(self, values):
        # Check if critical fields are being modified
        critical_fields = ["product_id", "product_qty", "product_uom_id"]
        if any(field in values for field in critical_fields):
            for bom_line in self:
                bom = bom_line.bom_id
                # Check for existing production orders
                production_orders = self.env["mrp.production"].search(
                    [("bom_id", "=", bom.id), ("state", "not in", ["cancel"])], limit=5
                )
                if production_orders:
                    production_names = ", ".join(production_orders.mapped("name"))
                    raise UserError(
                        "Cannot modify BOM line '%s' for BOM '%s'. "
                        "There are active or done production orders: %s. "
                        "Please complete or cancel these production orders"
                        " before modifying the BOM line."
                    ) % (bom_line.display_name, bom.display_name, production_names)

        return super().write(values)

    def unlink(self):
        for bom_line in self:
            bom = bom_line.bom_id
            # Check for existing production orders before deletion
            production_orders = self.env["mrp.production"].search(
                [("bom_id", "=", bom.id), ("state", "not in", ["done", "cancel"])]
            )

            if production_orders:
                production_names = ", ".join(production_orders.mapped("name"))
                raise UserError(
                    "Cannot delete BOM line '%s' from BOM '%s'. "
                    "There are active production orders: %s. "
                    "Please complete or cancel these production orders "
                    "before removing the BOM line."
                ) % (bom_line.display_name, bom.display_name, production_names)

        return super().unlink()
