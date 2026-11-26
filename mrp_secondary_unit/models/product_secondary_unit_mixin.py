# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare

DERIVED_DEPENDENCY_TYPES = ("dependent", "secondary_priority")


class ProductSecondaryUnitMixin(models.AbstractModel):
    _inherit = "product.secondary.unit.mixin"

    def _derive_secondary_uom_qty(self):
        """Set the secondary quantity from the quantity, unless the unit is
        independent; the inherited helper skips secondary-priority units."""
        for record in self:
            if not record.secondary_uom_id:
                record.secondary_uom_qty = 0.0
            elif record.secondary_uom_id.dependency_type in DERIVED_DEPENDENCY_TYPES:
                record.secondary_uom_qty = record._convert_qty_to_secondary_uom(
                    record._get_quantity_from_line()
                )

    def _keep_qty_matching_secondary(self):
        """Keep the quantity of the records whose secondary quantity is the
        quantity converted, and return the other records.

        Converting such a secondary quantity back would only apply its rounding.
        """
        kept = self.filtered(
            lambda r: r.secondary_uom_id.dependency_type in DERIVED_DEPENDENCY_TYPES
            and not float_compare(
                r._convert_qty_to_secondary_uom(r._get_quantity_from_line()),
                r.secondary_uom_qty,
                precision_rounding=r.secondary_uom_id.uom_id.rounding,
            )
        )
        for record in kept:
            qty_field = record._secondary_unit_fields["qty_field"]
            record[qty_field] = record[qty_field]
        return self - kept
