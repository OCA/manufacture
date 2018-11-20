# Copyright 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Product(models.Model):
    _inherit = 'product.product'

    llc = fields.Integer(string='Low Level Code', default=0)
    manufacturing_order_ids = fields.One2many(
        comodel_name='mrp.production',
        inverse_name='product_id',
        string='Manufacturing Orders',
        domain=[('state', '=', 'draft')],
    )
    purchase_order_line_ids = fields.One2many(
        comodel_name='purchase.order.line',
        inverse_name='product_id',
        string='Purchase Orders',
    )
    mrp_area_ids = fields.One2many(
        comodel_name='product.mrp.area',
        inverse_name='product_id',
        string='MRP Area parameters'
    )
    mrp_area_count = fields.Integer(
        string='MRP Area Parameter Count',
        readonly=True,
        compute='_compute_mrp_area_count')

    @api.multi
    def _compute_mrp_area_count(self):
        for rec in self:
            rec.mrp_area_count = len(rec.mrp_area_ids)

    @api.multi
    def action_view_mrp_area_parameters(self):
        self.ensure_one()
        action = self.env.ref('mrp_multi_level.product_mrp_area_action')
        result = action.read()[0]
        product_ids = self.ids
        if len(product_ids) > 1:
            result['domain'] = [('product_id', 'in', product_ids)]
        else:
            res = self.env.ref('mrp_multi_level.product_mrp_area_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = product_ids[0]
        result['context'] = {'default_product_id': product_ids[0]}
        return result
