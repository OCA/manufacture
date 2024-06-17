# Copyright 2024 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import datetime

from odoo import fields, models


class MrpProduction2(models.Model):
    _inherit = "mrp.production"

    update_expiration_date = fields.Boolean(
        help="Updates expiration date of lot based on planned date", default=True
    )

    def write(self, vals):
        res = super().write(vals)
        if not self.update_expiration_date:
            return res
        if "date_planned_start" in vals or "lot_producing_id" in vals:
            for production in self:
                expiration_time = (
                    production.lot_producing_id.product_id.product_tmpl_id.expiration_time
                )
                production.lot_producing_id.expiration_date = (
                    production.date_planned_start
                    + datetime.timedelta(days=expiration_time)
                )
        return res
