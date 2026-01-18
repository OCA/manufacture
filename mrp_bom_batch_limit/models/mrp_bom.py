# Copyright 2025 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    enable_batch_limit = fields.Boolean(
        help="Batch size limits",
    )
    min_batch_qty = fields.Float(
        string="Min Batch Quantity",
        digits="Product Unit",
        help="Minimum quantity for production orders",
    )
    max_batch_qty = fields.Float(
        string="Max Batch Quantity",
        digits="Product Unit",
        help="Maximum quantity for production orders",
    )

    @api.constrains("min_batch_qty", "max_batch_qty")
    def _check_batch_limits(self):
        for bom in self.filtered("enable_batch_limit"):
            if bom.min_batch_qty < 0:
                raise ValidationError(_("The minimum batch quantity must be positive!"))
            if bom.max_batch_qty < 0:
                raise ValidationError(_("The maximum batch quantity must be positive!"))
            if (
                bom.min_batch_qty
                and bom.max_batch_qty
                and bom.min_batch_qty > bom.max_batch_qty
            ):
                raise ValidationError(
                    _(
                        "The minimum batch quantity cannot be greater"
                        " than the maximum batch quantity!"
                    )
                )
