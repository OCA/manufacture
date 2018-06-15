# -*- coding: utf-8 -*-

from odoo import models, fields


class StockMove(models.Model):
    """Extend to add method `_update_unit_factor`."""

    _inherit = 'stock.move'

    # Force numeric with unlimited precision. We need it to make sure
    # it converts to correct quantity.
    unit_factor = fields.Float(digits=0.0)

    def _update_unit_factor(self, orig_quantity):
        self.ensure_one()
        self.unit_factor = self.product_uom_qty / orig_quantity
