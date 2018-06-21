# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo import exceptions


class MrpMove(models.Model):
    _name = 'mrp.move'
    _order = 'mrp_product_id, mrp_date, mrp_type desc, id'

    # TODO: too many indexes...

    mrp_area_id = fields.Many2one('mrp.area', 'MRP Area')
    current_date = fields.Date('Current Date')
    current_qty = fields.Float('Current Qty')
    # TODO: remove purchase request and move to other module?
    # TODO: cancel is not needed I think...
    mrp_action = fields.Selection(
        selection=[('mo', 'Manufacturing Order'),
                   ('po', 'Purchase Order'),
                   ('pr', 'Purchase Request'),
                   ('so', 'Sale Order'),
                   ('cancel', 'Cancel'),
                   ('none', 'None')],
        string='Action',
    )
    mrp_action_date = fields.Date('MRP Action Date')
    mrp_date = fields.Date('MRP Date')
    mrp_move_down_ids = fields.Many2many(
        comodel_name='mrp.move',
        relation='mrp_move_rel',
        column1='move_up_id',
        column2='move_down_id',
        string='MRP Move DOWN',
    )
    mrp_move_up_ids = fields.Many2many(
        comodel_name='mrp.move',
        relation='mrp_move_rel',
        column1='move_down_id',
        column2='move_up_id',
        string='MRP Move UP',
    )
    mrp_minimum_stock = fields.Float(
        string='Minimum Stock',
        related='product_id.mrp_minimum_stock',
    )
    mrp_order_number = fields.Char('Order Number')
    # TODO: move purchase request to another module
    mrp_origin = fields.Selection(
        selection=[('mo', 'Manufacturing Order'),
                   ('po', 'Purchase Order'),
                   ('pr', 'Purchase Request'),
                   ('so', 'Sale Order'),
                   ('mv', 'Move'),
                   ('fc', 'Forecast'), ('mrp', 'MRP')],
        string='Origin')
    mrp_processed = fields.Boolean('Processed')
    mrp_product_id = fields.Many2one('mrp.product', 'Product', index=True)
    mrp_qty = fields.Float('MRP Quantity')
    mrp_type = fields.Selection(
        selection=[('s', 'Supply'), ('d', 'Demand')],
        string='Type',
    )
    name = fields.Char('Description')
    parent_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Parent Product', index=True,
    )
    product_id = fields.Many2one('product.product',
                                 'Product', index=True)
    production_id = fields.Many2one('mrp.production',
                                    'Manufacturing Order', index=True)
    purchase_line_id = fields.Many2one('purchase.order.line',
                                       'Purchase Order Line', index=True)
    purchase_order_id = fields.Many2one('purchase.order',
                                        'Purchase Order', index=True)
    running_availability = fields.Float('Running Availability')
    sale_line_id = fields.Many2one('sale.order.line',
                                   'Sale Order Line', index=True)
    sale_order_id = fields.Many2one('sale.order', 'Sale Order', index=True)
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
    stock_move_id = fields.Many2one('stock.move', 'Stock Move', index=True)

    @api.model
    def mrp_production_prepare(self, bom_id, routing_id):
        return {
            'product_uos_qty': 0.00,
            'product_uom': self.product_id.product_tmpl_id.uom_id.id,
            'product_qty': self.mrp_qty,
            'product_id': self.product_id.id,
            'location_src_id': 12,
            'date_planned': self.mrp_date,
            'cycle_total': 0.00,
            'company_id': 1,
            'state': 'draft',
            'hour_total': 0.00,
            'bom_id': bom_id,
            'routing_id': routing_id,
            'allow_reorder': False
        }

    @api.model
    def mrp_process_mo(self):
        if self.mrp_action != 'mo':
            return True
        bom_id = False
        routing_id = False
        mrp_boms = self.env['mrp.bom'].search(
            [('product_id', '=', self.product_id.id),
             ('type', '=', 'normal')], limit=1)
        for mrp_bom in mrp_boms:
            bom_id = mrp_bom.id
            routing_id = mrp_bom.routing_id.id

        if self.product_id.track_production and self.mrp_qty > 1:
            raise exceptions.Warning(_('Not allowed to create '
                                       'manufacturing order with '
                                       'quantity higher than 1 '
                                       'for serialized product'))
        else:
            production_data = self.mrp_production_prepare(bom_id, routing_id)
            pr = self.env['mrp.production'].create(production_data)
            self.production_id = pr.id
            self.current_qty = self.mrp_qty
            self.current_date = self.mrp_date
            self.mrp_processed = True
            self.name = pr.name

    # TODO: extension to purchase requisition in other module?
    @api.model
    def mrp_process_pr(self):
        if self.mrp_action != 'pr':
            return True
        seq = self.env['ir.sequence'].search(
            [('code', '=', 'purchase.order.requisition')])
        seqnbr = self.env['ir.sequence'].next_by_id(seq.id)
        self.env['purchase.requisition'].create({
            'origin': 'MRP - [' + self.product_id.default_code + '] ' +
                      self.product_id.name,
            'exclusive': 'exclusive',
            'message_follower_ids': False,
            'date_end': False,
            'date_start': self.mrp_date,
            'company_id': 1,
            'warehouse_id': 1,
            'state': 'draft',
            'line_ids':  [[0, False,
                           {'product_uom_id':
                                self.product_id.product_tmpl_id.uom_id.id,
                            'product_id': self.product_id.id,
                            'product_qty': self.mrp_qty,
                            'name': self.product_id.name}]],
            'message_ids': False,
            'description': False,
            'name': seqnbr
        })
        self.current_qty = self.mrp_qty
        self.current_date = self.mrp_date
        self.mrp_processed = True
        self.name = seqnbr
