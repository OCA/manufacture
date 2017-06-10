# -*- coding: utf-8 -*-
# Copyright 2017 Bima Wijaya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_from_move(self):
        res = super(StockMove, self)._prepare_procurement_from_move()
        if res and self.procurement_id and self.procurement_id.property_ids:
            res['property_ids'] = [(6, 0,
                                    self.procurement_id.property_ids.ids)]
        return res

    def action_explode(self):
        """ Explodes pickings.
        @param move: Stock moves
        @return: True
        """
        property_ids = self.procurement_id.sale_line_id.property_ids.ids
        return super(StockMove, self.with_context(
            property_ids=property_ids)).action_explode()