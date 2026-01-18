# Copyright 2025 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    batch_limit_warning = fields.Boolean(
        compute="_compute_batch_limit_warning",
    )
    batch_limit_message = fields.Char(
        compute="_compute_batch_limit_warning",
    )

    @api.depends("product_qty", "bom_id")
    def _compute_batch_limit_warning(self):
        for production in self:
            production.batch_limit_warning = False
            production.batch_limit_message = ""

            if not production.bom_id or not production.bom_id.enable_batch_limit:
                continue

            bom = production.bom_id
            qty = production.product_qty

            if qty < bom.min_batch_qty and bom.min_batch_qty:
                production.batch_limit_warning = True
                production.batch_limit_message = _(
                    "Quantity (%(qty).2f) is below"
                    " minimum batch quantity (%(min_qty).2f)."
                ) % {"qty": qty, "min_qty": bom.min_batch_qty}
            elif qty > bom.max_batch_qty and bom.max_batch_qty:
                production.batch_limit_warning = True
                production.batch_limit_message = _(
                    "Quantity (%(qty).2f) exceeds"
                    " maximum batch quantity (%(max_qty).2f)."
                ) % {"qty": qty, "max_qty": bom.max_batch_qty}

    def action_confirm(self):
        for production in self:
            if production.batch_limit_warning:
                raise UserError(production.batch_limit_message)
        return super().action_confirm()
