# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class MrpMove(models.Model):
    _name = 'mrp.move'
    _order = 'product_mrp_area_id, mrp_date, mrp_type desc, id'

    # TODO: too many indexes...

    product_mrp_area_id = fields.Many2one(
        comodel_name="product.mrp.area",
        string="Product", index=True,
        required=True,
    )
    mrp_area_id = fields.Many2one(
        comodel_name="mrp.area",
        related="product_mrp_area_id.mrp_area_id",
        string="MRP Area",
        store=True,
        index=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        related='product_mrp_area_id.product_id',
        store=True,
    )

    current_date = fields.Date(string='Current Date')
    current_qty = fields.Float(string='Current Qty')
    mrp_date = fields.Date(string='MRP Date')
    planned_order_up_ids = fields.Many2many(
        comodel_name="mrp.planned.order",
        relation="mrp_move_planned_order_rel",
        column1="move_down_id",
        column2="order_id",
        string="Planned Orders UP",
    )
    mrp_order_number = fields.Char(string='Order Number')
    mrp_origin = fields.Selection(
        selection=[('mo', 'Manufacturing Order'),
                   ('po', 'Purchase Order'),
                   ('mv', 'Move'),
                   ('fc', 'Forecast'),
                   ('mrp', 'MRP')],
        string='Origin')
    mrp_qty = fields.Float(string='MRP Quantity')
    mrp_type = fields.Selection(
        selection=[('s', 'Supply'), ('d', 'Demand')],
        string='Type',
    )
    name = fields.Char(string='Description')
    parent_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Parent Product", index=True,
    )
    production_id = fields.Many2one(
        comodel_name='mrp.production',
        string='Manufacturing Order', index=True,
    )
    purchase_line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        string='Purchase Order Line', index=True,
    )
    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order', index=True,
    )
    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('assigned', 'Assigned'),
                   ('confirmed', 'Confirmed'),
                   ('waiting', 'Waiting'),
                   ('partially_available', 'Partially Available'),
                   ('ready', 'Ready'),
                   ('sent', 'Sent'),
                   ('to approve', 'To Approve'),
                   ('approved', 'Approved')],
        string='State',
    )
    stock_move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Stock Move', index=True,
    )
