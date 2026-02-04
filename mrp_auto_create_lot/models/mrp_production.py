# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models
from odoo.tools import float_is_zero


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _set_auto_lot_producing(self):
        """Assign the lot_producing_id automatically using the lot sequence"""
        for production in self:
            if (
                production.product_id.tracking == "none"
                or not production.picking_type_id.auto_create_lot
                or (
                    not production.product_id.auto_create_lot
                    and not production.product_id.categ_id.auto_create_lot
                )
                or production.lot_producing_id
                or float_is_zero(
                    production.qty_producing,
                    precision_rounding=production.product_uom_id.rounding,
                )
            ):
                continue
            production.action_generate_serial()

    def button_mark_done(self):
        self._set_auto_lot_producing()
        return super().button_mark_done()
