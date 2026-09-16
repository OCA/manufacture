# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _prepare_stock_lot_values(self):
        self.ensure_one()
        lot_sequence = self.product_id.product_tmpl_id.lot_sequence_id
        if self.env["stock.lot"]._get_sequence_policy() == "product" and lot_sequence:
            # Avoid consuming the global sequence before using the product sequence.
            name = self.env["stock.lot"]._get_next_serial(
                self.company_id,
                self.product_id,
            )
            if not name:
                raise UserError(
                    _("Please set the first Serial Number or a default sequence")
                )
            vals = {
                "product_id": self.product_id.id,
                "company_id": self.company_id.id,
                "name": name,
            }
        else:
            vals = super()._prepare_stock_lot_values()
        return vals
