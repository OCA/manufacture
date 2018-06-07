# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.product'
    
    llc = fields.Integer('Low Level Code', default=0)
    manufacturing_order_ids = fields.One2many('mrp.production',
                                              'product_id',
                                              'Manufacturing Orders',
                                              domain=[('state', '=', 'draft')])
    mrp_applicable = fields.Boolean('MRP Applicable')
    mrp_exclude = fields.Boolean('Exclude from MRP')
    mrp_inspection_delay = fields.Integer('Inspection Delay', default=0)
    mrp_lead_time = fields.Integer('Lead Time', default=1)
    mrp_maximum_order_qty = fields.Float('Maximum Order Qty', default=0.00)
    mrp_minimum_order_qty = fields.Float('Minimum Order Qty', default=0.00)
    mrp_minimum_stock = fields.Float('Minimum Stock')
    mrp_nbr_days = fields.Integer('Nbr. Days', default=0,
                                  help="Number of days to group demand for "
                                       "this product during the MRP run, "
                                       "in order to determine the quantity "
                                       "to order.")
    mrp_product_ids = fields.One2many('mrp.product',
                                      'product_id', 'MRP Product data')
    mrp_qty_multiple = fields.Float('Qty Multiple', default=1.00)
    mrp_transit_delay = fields.Integer('Transit Delay', default=0)
    mrp_verified = fields.Boolean('Verified for MRP',
                                  help="Identifies that this product has "
                                       "been verified to be valid for the "
                                       "MRP.")
    purchase_order_line_ids = fields.One2many('purchase.order.line',
                                              'product_id', 'Purchase Orders')
    purchase_requisition_ids = fields.One2many('purchase.requisition.line',
                                               'product_id',
                                               'Purchase Requisitions')
