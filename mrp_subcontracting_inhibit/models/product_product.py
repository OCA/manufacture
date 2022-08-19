# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_sellers(self, params=False):
        res = super()._prepare_sellers(params)
        return res.filtered(
            lambda x: x.subcontracting_inhibit
            == bool(self.env.context.get("subcontracting_inhibit"))
        )
