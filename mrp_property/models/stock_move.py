# coding: utf-8
# Copyright 2008 - 2016 Odoo S.A.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _prepare_procurement_from_move(self):
        """ The procurement that creates the MO might not be the original
        procurement. Therefore, propagate the properties further down. """
        res = super(StockMove, self)._prepare_procurement_from_move()
        if self.procurement_id.property_ids:
            res['property_ids'] = [
                (6, 0, self.procurement_id.property_ids.ids)]
        return res

    @api.multi
    def action_explode(self):
        """ Pass the properties from the procurement in the context for the
        selection of the right BoM """
        properties = self.procurement_id.sale_line_id.property_ids
        if properties:
            self = self.with_context(property_ids=properties.ids)
        return super(StockMove, self).action_explode()
