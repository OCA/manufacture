# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.constrains("tracking")
    def _check_bom_propagate_lot_number(self):
        for product in self:
            product.product_tmpl_id._check_bom_propagate_lot_number()
