# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_round


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    @api.constrains("product_qty", "product_uom_id")
    def _check_product_qty_uom_rounding(self):
        for line in self:
            if not line.product_uom_id or not line.product_qty:
                continue
            rounding = line.product_uom_id.rounding
            rounded_qty = float_round(line.product_qty, precision_rounding=rounding)
            if line.product_qty != rounded_qty:
                raise ValidationError(
                    _(
                        "The quantity %(qty)s for component '%(product)s' does not "
                        "respect the rounding precision (%(rounding)s) of the Unit of "
                        "Measure '%(uom)s'. "
                        "Please adjust the quantity to a valid value.",
                        qty=line.product_qty,
                        product=line.product_id.display_name,
                        rounding=rounding,
                        uom=line.product_uom_id.name,
                    )
                )
