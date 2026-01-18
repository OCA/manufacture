# Copyright 2025 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    batch_size = fields.Float(
        default=1.0,
        digits="Product Unit",
        help="All automatically generated manufacturing orders for this product "
        "will be of this size.",
    )
    enable_batch_size = fields.Boolean(
        default=False, help="Enable batch size for automatic manufacturing orders"
    )

    @api.constrains("enable_batch_size", "batch_size")
    def _check_valid_batch_size(self):
        for bom in self:
            if (
                bom.enable_batch_size
                and float_compare(
                    bom.batch_size, 0.0, precision_rounding=bom.product_uom_id.rounding
                )
                <= 0
            ):
                raise ValidationError(_("The batch size must be positive!"))
