# Copyright 2025 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends("bom_id")
    def _compute_product_qty(self):
        """Override to suggest batch size when BoM has batch size enabled"""
        super()._compute_product_qty()
        for production in self:
            if (
                production.bom_id
                and production.bom_id.enable_batch_size
                and production.state == "draft"
            ):
                # Convert batch size to the MO's UOM if needed
                batch_size = production.bom_id.product_uom_id._compute_quantity(
                    production.bom_id.batch_size,
                    production.product_uom_id or production.bom_id.product_uom_id,
                )
                production.product_qty = batch_size
        return
