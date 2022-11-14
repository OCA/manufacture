# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# - Joan Sisquella Andrés <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _get_inventory_fields_write(self):
        """
        Adding field product_uom_id, inventory_quantity
        """
        fields = super(StockQuant, self)._get_inventory_fields_write()
        return fields + ["product_uom_id", "inventory_quantity"]
