# -*- coding: utf-8 -*-
# Copyright 2017 Bima Wijaya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    property_ids = fields.Many2many('mrp.property',
                                    'sale_order_line_property_rel', 'order_id',
                                    'property_id', 'Properties', readonly=True,
                                    states={'draft': [('readonly', False)]})

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id)
        vals['property_ids'] = [(6, 0, self.property_ids.ids)]
        return vals
