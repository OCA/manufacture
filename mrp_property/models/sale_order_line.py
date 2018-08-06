# coding: utf-8
# Copyright 2008 - 2016 Odoo S.A.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    property_ids = fields.Many2many(
        'mrp.property', 'sale_order_line_property_rel', 'order_id',
        'property_id', 'Properties', readonly=True,
        help=("If a production product is manufactured for this sale order, "
              "the BoM that has the same properties as the sale order line "
              "will be selected (a BoM with no properties at all could be "
              "selected as a fallback"),
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]})

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        """ Add the properties of the sale order line to the procurement
        that is generated from it """
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id)
        vals['property_ids'] = [(6, 0, self.property_ids.ids)]
        return vals

    @api.multi
    def _get_delivered_qty(self):
        """ Make sure that the correct phantom bom is selected in the super
        method (if any) """
        self.ensure_one()
        if self.property_ids:
            self = self.with_context(property_ids=self.property_ids.ids)
        return super(SaleOrderLine, self)._get_delivered_qty()
