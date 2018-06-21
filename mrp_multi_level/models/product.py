# Copyright 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.product'

    llc = fields.Integer(string='Low Level Code', default=0)
    manufacturing_order_ids = fields.One2many(
        comodel_name='mrp.production',
        inverse_name='product_id',
        string='Manufacturing Orders',
        domain=[('state', '=', 'draft')],
    )
    # TODO: applicable and exclude... redundant??
    mrp_applicable = fields.Boolean(string='MRP Applicable')
    mrp_exclude = fields.Boolean(string='Exclude from MRP')
    mrp_inspection_delay = fields.Integer(string='Inspection Delay')
    mrp_maximum_order_qty = fields.Float(
        string='Maximum Order Qty', default=0.0,
    )
    mrp_minimum_order_qty = fields.Float(
        string='Minimum Order Qty', default=0.0,
    )
    mrp_minimum_stock = fields.Float(string='Minimum Stock')
    mrp_nbr_days = fields.Integer(
        string='Nbr. Days', default=0,
        help="Number of days to group demand for this product during the "
             "MRP run, in order to determine the quantity to order.",
    )
    mrp_product_ids = fields.One2many(
        comodel_name='mrp.product',
        inverse_name='product_id',
        string='MRP Product data',
    )
    mrp_qty_multiple = fields.Float(string='Qty Multiple', default=1.00)
    mrp_transit_delay = fields.Integer(string='Transit Delay', default=0)
    mrp_verified = fields.Boolean(
        string='Verified for MRP',
        help="Identifies that this product has been verified "
             "to be valid for the MRP.",
    )
    purchase_order_line_ids = fields.One2many(
        comodel_name='purchase.order.line',
        inverse_name='product_id',
        string='Purchase Orders',
    )
