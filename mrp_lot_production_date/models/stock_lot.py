# Copyright 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    def _set_expiration_date_from_production(self):
        """Set expiration dates based on production date."""
        for lot in self.filtered(
            lambda x: x.production_date and x.product_id.use_expiration_date
        ):
            tmpl = lot.product_id.product_tmpl_id
            # Calculate expiration date from production date
            lot.expiration_date = lot.production_date + timedelta(
                days=tmpl.expiration_time
            )
            # Recalculate other dates if expiration date exists
            lot.use_date = lot.expiration_date - timedelta(days=tmpl.use_time)
            lot.removal_date = lot.expiration_date - timedelta(days=tmpl.removal_time)
            lot.alert_date = lot.expiration_date - timedelta(days=tmpl.alert_time)

    @api.model_create_multi
    def create(self, vals_list):
        lots = super().create(vals_list)
        if any("production_date" in vals for vals in vals_list):
            lots._set_expiration_date_from_production()
        return lots

    def write(self, vals):
        super().write(vals)
        if "production_date" in vals:
            self._set_expiration_date_from_production()
        return True
