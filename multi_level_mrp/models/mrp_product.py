# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduct(models.Model):
    _name = 'mrp.product'

    mrp_area_id = fields.Many2one('mrp.area', 'MRP Area')
    current_qty_available = fields.Float(string='Current Qty Available',
                                         related='product_id.qty_available')
    main_supplier_id = fields.Many2one('res.partner', 'Main Supplier',
                                       select=True)
    mrp_inspection_delay = fields.Integer(
        string='Inspection Delay', related='product_id.mrp_inspection_delay')
    mrp_lead_time = fields.Float(string='Lead Time',
                                   related='product_id.produce_delay')
    mrp_llc = fields.Integer('Low Level Code', select=True)
    mrp_maximum_order_qty = fields.Float(
        string='Maximum Order Qty', related='product_id.mrp_maximum_order_qty')
    mrp_minimum_order_qty = fields.Float(
        string='Minimum Order Qty', related='product_id.mrp_minimum_order_qty')
    mrp_minimum_stock = fields.Float(string='Minimum Stock',
                                     related='product_id.mrp_minimum_stock')
    mrp_move_ids = fields.One2many('mrp.move', 'mrp_product_id', 'MRP Moves')
    mrp_nbr_days = fields.Integer(
        string='Nbr. Days', related='product_id.mrp_nbr_days')
    mrp_qty_available = fields.Float('MRP Qty Available')
    mrp_qty_multiple = fields.Float(string='Qty Multiple',
                                    related='product_id.mrp_qty_multiple')
    # TODO: this was: mrp_transit_delay = fields.Integer(mrp_move_ids) ??¿?¿¿?
    mrp_transit_delay = fields.Integer(related = 'product_id.mrp_transit_delay')
    mrp_verified = fields.Boolean(string='MRP Verified',
                                  related='product_id.mrp_verified')
    name = fields.Char('Description')
    nbr_mrp_actions = fields.Integer('Nbr Actions', select=True)
    nbr_mrp_actions_4w = fields.Integer('Nbr Actions 4 Weeks', select=True)
    product_id = fields.Many2one('product.product', 'Product', select=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template',
                                      related='product_id.product_tmpl_id')
    # TODO: extension to purchase requisition in other module?
    # purchase_requisition = fields.Boolean(string='Purchase Requisition',
    #                                       related='product_id.purchase_requisition')
    supply_method = fields.Selection((('buy', 'Buy'),
                                      ('produce', 'Produce')),
                                     'Supply Method')
