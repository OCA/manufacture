# Copyright 2019 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"
    # New fields:
    #   delivery_done_count - # of linked pickings in done state
    #   manufacturing_type  - Type of manufacturing (internal or external)
    #                           Note : external means that manufacturing order
    #                                  is subcontracted
    #   purchase_ids        - Linked RFQ / Purchase Orders
    #   purchase_count      - # of linked RFQ / Purchase Orders
    #   purchase_done_count - # of linked Purchase Orders in completed or
    #                           cancelled state
    #   service_id          - Service to be subcontracted
    #   subcontractor_id    - Partner to whom Manufacturing Order would be
    #                           subcontracted
    delivery_done_count = fields.Integer(string='# Done Delivery Orders',
                                         compute='_compute_picking_ids')
    manufacturing_type = fields.Selection(
        [('internal', 'Internal Manufacturing'),
         ('external', 'External Manufacturing (subcontracted)')],
        string='Type of Manufacturing',
        default="internal",
        readonly=True)
    purchase_ids = fields.Many2many('purchase.order',
                                    compute='_compute_purchase_ids',
                                    string='Purchase Order associated \
                                        to this manufacturing order')
    purchase_count = fields.Integer(string='# Purchase Orders',
                                    compute='_compute_purchase_ids')
    purchase_done_count = fields.Integer(string='# Done Purchase Orders',
                                         compute='_compute_purchase_ids')
    service_id = fields.Many2one(
        'product.product',
        domain=([('product_tmpl_id.type_subcontracting', '=', True)]),
        string='Service',
        help="Service linked to this operation",
        readonly=True)
    subcontractor_id = fields.Many2one(
        'res.partner',
        domain=([('subcontractor', '=', True)]),
        string='Subcontractor',
        readonly=True)

    @api.depends('name')
    def _compute_purchase_ids(self):
        # Links RFQ / Purchase Orders to this Manufacturing order
        # (purchase_ids)
        # Counts number of RFQ / Purchase Orders linked (purchase_count)
        # Counts number of completed or cancelled Purchase Orders Linked
        #   (purchase_done_count)
        for order in self:
            order.purchase_ids = self.env['purchase.order'].search([
                ('origin', 'ilike', order.name),
            ])
            order.purchase_count = len(order.purchase_ids)
            order.purchase_done_count = len(
                order.purchase_ids.filtered(lambda r: r.state in ['purchase',
                                                                  'done',
                                                                  'cancel']))

    @api.depends('procurement_group_id', 'purchase_ids')
    def _compute_picking_ids(self):
        # Overloads existing method from mrp module, with the following:
        # - Extends linked Pickings to the ones related to Purchase Orders
        #   (delivery of purchase orders) where Manufacturing Order is present
        #   in the name of the PO (picking_ids)
        # - Counts the new total of related Pickings (delivery_count)
        # - Counts number of done related Pickings (delivery_done_count)
        for order in self:
            procurement_groups_ids = self.env['procurement.group'].search([
                '|',
                ('id', '=', order.procurement_group_id.id),
                ('name', 'in', order.purchase_ids.mapped('name')),
                ]).ids
            order.picking_ids = self.env['stock.picking'].search([
                ('group_id', 'in', procurement_groups_ids),
            ])
            order.delivery_count = len(order.picking_ids)
            order.delivery_done_count = len(
                order.picking_ids.filtered(lambda r: r.state in ['done',
                                                                 'cancel']))

    def action_view_mo_purchase(self):
        # Retrieves action to display lines of RFQ / Purchase Orders related to
        # the current Manufacturing Order (displayed when clicking on Purchases
        # button on Manufacturing Order view form)
        # Returns:
        #    [action] -- Display list of purchase Orders related to this MO
        self.ensure_one()
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        purchases = self.mapped('purchase_ids')
        if len(purchases) > 1:
            action['domain'] = [('id', 'in', purchases.ids)]
        elif purchases:
            action['views'] = [(
                self.env.ref('purchase.purchase_order_form').id,
                'form'
                )]
            action['res_id'] = purchases.id
        return action

    @api.multi
    def subcontract_mo(self):
        # Retrieves action to create wizard for subcontracting Manufacturing
        # Order
        # This action is called from the Subcontract Order button in
        # Manufacturing Order form view
        # Returns:
        #    [action] -- Wizard mrp_subcontract
        self.ensure_one()
        action = self.env.ref(
            'mrp_subcontract_mo.act_mrp_subcontract').read()[0]
        return action

    @api.multi
    def post_inventory(self):
        # Overloads existing method from mrp module, with the following:
        # - If manufacturing Order is subcontracted, when posting the inventory
        #   moves (moving manufactured product(s) from Virtual Location >
        #   Production to Subcontractor Location), the picking(s) to retrieve
        #   manufactured product(s) from subcontractor are confirmed and
        #   availability of products is checked.
        super(MrpProduction, self).post_inventory()
        # Retrieves Return picking type created in data/picking_type.xml
        return_picking_type = self.env.ref(
            "mrp_subcontract_mo.picking_type_receipt_subcontracting")
        for order in self:
            # If MO is subcontracted:
            if order.manufacturing_type in ['external']:
                # For each picking of type return_picking in linked pickings
                for return_picking in order.picking_ids.filtered(
                        lambda r: r.picking_type_id == return_picking_type):
                    # Confirm picking
                    return_picking.action_confirm()
                    # Check availability of products
                    return_picking.action_assign()
        return True

    def _generate_delivery_picking(self):
        # Generates automatically picking for delivery of raw materials to
        #   Subcontractor
        # Updates source location for manufacturing raw products to
        #     subcontractor location
        # Unreserve products for manufacturing (since they first need to be
        #   shipped to subcontractor)
        # Confirm new picking and check for availability

        # Retrieves Delivery picking type created in data/picking_type.xml
        delivery_picking_type = self.env.ref(
            "mrp_subcontract_mo.picking_type_delivery_subcontracting")
        # Retrieves Local stock location
        local_stock = self.env.ref("stock.stock_location_stock")

        # Generate delivery picking with :
        # - picking_type = Delivery to Subcontractor
        # - partner_id = Selected Subcontractor
        # - date = now
        # - origin = Manufacturing Order name
        # - location_id (where to take the products from) = local stock
        # - location_dest_id (where to send products) = Manufacturing Order raw
        #     materials location (= subcontractor location forced in
        #     mrp_subcontract wizard)
        # - company_id = current user company
        # - state = waiting (waiting for products to be available)
        delivery_picking = self.env['stock.picking'].create({
            'picking_type_id': delivery_picking_type.id,
            'partner_id': self.subcontractor_id.id,
            'date': str(datetime.now()),
            'origin': self.name,
            'location_id': local_stock.id,
            'location_dest_id': self.location_src_id.id,
            'company_id': self.env.user.company_id.id,
            'state': 'waiting'
            })
        # Generate delivery stock moves associated to above created picking
        #     from move_raw_ids related to current Manufacturing Order
        #     (listing all products necessary to manufacture) with:
        # - name = move_raw_id name
        # - location_id (where to take the products from) = local stock
        # - location_dest_id (where to send products) = Manufacturing Order raw
        #     materials location (= subcontractor location forced in
        #     mrp_subcontract wizard)
        # - partner_id = Selected Subcontractor
        # - move_orig_ids (previous move(s) for chaining moves) = move_orig_ids
        #     from move_raw_id
        # - move_dest_ids (next move(s) for chaining moves) = move_raw_id
        # - product_id = move_raw_id product id
        # - product_uom_qty (necessary quantity) = move_raw_id product uom qty
        # - product_uom (product unit of measure) = move_raw_id product uom
        # - price_unit (price of product) = move_raw_id price unit
        # - group_id (purchase group) = move_raw_id group id
        # - created_purchase_line_id (related purchase line for buying missing
        #     raw products) = move_raw_id created purchase line id
        for move in self.move_raw_ids:
            new_move = self.env['stock.move'].create({
                'name': move.name,
                'location_id': local_stock.id,
                'location_dest_id': self.location_src_id.id,
                'partner_id': self.subcontractor_id.id,
                'picking_type_id': delivery_picking_type.id,
                'picking_id': delivery_picking.id,
                'move_orig_ids': [(6, 0, move.move_orig_ids.ids)],
                'move_dest_ids': [(4, move.id)],
                'product_id': move.product_id.id,
                'product_uom_qty': move.product_uom_qty,
                'product_uom': move.product_uom.id,
                'price_unit': move.price_unit,
                'group_id': move.group_id.id,
                'created_purchase_line_id': move.created_purchase_line_id.id,
                })
            # Update move_raw_id with:
            # - move_orig_ids (previous move(s) for chaining moves) = delivery
            #     # move (The production can only start once raw products are
            #     # delivered at subcontractor location)
            # - location_id (where to take the products from for starting
            #     # production) = Manufacturing Order raw materials location
            #     # (= subcontractor location forced in mrp_subcontract wizard)
            # - Remove related purchase line since now linked to delivery move
            move.write(({
                'move_orig_ids': [(5, 0, 0), (4, new_move.id)],
                'state': 'waiting',
                'location_id': self.location_src_id.id,
                'created_purchase_line_id': '',
            }))
            # Unreserve quantities for move_raw_id (since products first need
            # to be delivered to subcontractor location)
            move._do_unreserve()
            # Confirm picking
            new_move._action_confirm()
            # Check availability of products
            new_move._action_assign()

    def _generate_return_picking(self):
        # Generates automatically picking for return of manufactured materials
        #     from Subcontractor
        # Updates destination location of manufacturing move to subcontractor
        #     location

        # Retrieves Receipts picking type created in data/picking_type.xml
        return_picking_type = self.env.ref(
            "mrp_subcontract_mo.picking_type_receipt_subcontracting")
        # Retrieves Local stock location
        local_stock = self.env.ref("stock.stock_location_stock")

        # Generate return picking with :
        # - picking_type = Receipts from Subcontractor
        # - partner_id = Selected Subcontractor
        # - date = now
        # - origin = Manufacturing Order name
        # - location_id (where to take the products from) = Manufacturing Order
        #     finished materials location (= subcontractor location forced in
        #     mrp_subcontract wizard)
        # - location_dest_id (where to send products) = local stock
        # - company_id = current user company
        return_picking = self.env['stock.picking'].create({
            'picking_type_id': return_picking_type.id,
            'partner_id': self.subcontractor_id.id,
            'date': str(datetime.now()),
            'origin': self.name,
            'location_id': self.location_dest_id.id,
            'location_dest_id': local_stock.id,
            'company_id': self.env.user.company_id.id,
            })
        # Generate receipt stock moves associated to above created picking from
        #     move_finished_ids related to current Manufacturing Order (listing
        #     all products manufactured) with:
        # - name = move_finished_id name
        # - location_id (where to take the products from) = Manufacturing Order
        #     finished materials location (= subcontractor location forced in
        #     mrp_subcontract wizard)
        # - location_dest_id (where to send products) = local stock
        # - partner_id = Selected Subcontractor
        # - move_orig_ids (previous move(s) for chaining moves) =
        #     move_finished_id
        # - move_dest_ids (next move(s) for chaining moves) = move_orig_ids
        #     from move_finished_id
        # - product_id = move_finished_id product id
        # - product_uom_qty (necessary quantity) = move_finished_id product uom
        #     qty
        # - product_uom (product unit of measure)= move_finished_id product uom
        # - price_unit (price of product) = move_finished_id price unit
        # - group_id (purchase group) = move_finished_id group id
        for move in self.move_finished_ids:
            new_move = self.env['stock.move'].create({
                'name': move.name,
                'location_id': self.location_dest_id.id,
                'location_dest_id': local_stock.id,
                'partner_id': self.subcontractor_id.id,
                'picking_type_id': return_picking_type.id,
                'picking_id': return_picking.id,
                'production_id': '',
                'move_orig_ids': [(4, move.id)],
                'move_dest_ids': [(6, 0, move.move_dest_ids.ids)],
                'product_id': move.product_id.id,
                'product_uom_qty': move.product_uom_qty,
                'product_uom': move.product_uom.id,
                'price_unit': move.price_unit,
                'group_id': move.group_id.id,
                })

            # Update move_finished_id with:
            # - move_dest_ids (next move(s) for chaining moves) = receipt
            #     # move (The product can only be delivered back to local stock
            #     # once manufacturing is completed by subcontractor)
            # - location_dest_id (where to send manufactured products) =
            #     # Manufacturing Order finished materials location
            #     # (= subcontractor location forced in mrp_subcontract wizard)

            move.write(({
                'move_dest_ids': [(5, 0, 0), (4, new_move.id)],
                'location_dest_id': self.location_dest_id.id,
            }))

    def _generate_service_purchase(self):
        # Generates a purchase order to the subcontracted service
        # Retrieves payment term from subcontractor payment term
        payment_term = self.subcontractor_id\
            .property_supplier_payment_term_id
        service = self.service_id
        # Product template associated to selected service
        service_tmpl = service.product_tmpl_id
        # Price info retrieved for selected service and subcontractor
        service_supplier_infos = self.env[
            'product.supplierinfo'].search([
                ('product_tmpl_id', '=', service_tmpl.id),
                ('name', '=', self.subcontractor_id.id),
            ])
        # Creates purchase order with:
        # - partner_id = selected subcontractor
        # - company_id = current user company
        # - currency_id = subcontractor or company currency
        # - origin = manufacturing order name
        # - payment_term_id = subcontractor payment terms
        # - date_order = now
        # - lines of order = 1 x selected service with subcontractor price
        self.env['purchase.order'].create({
            'partner_id': self.subcontractor_id.id,
            'company_id': self.env.user.company_id.id,
            'currency_id': (
                self.subcontractor_id.currency_id.id
                or self.env.user.company_id.currency_id.id),
            'origin': self.name,
            'payment_term_id': payment_term.id,
            'date_order': str(datetime.now()),
            'order_line': [(0, 0, {
                'name': service.name,
                'product_qty': 1.0,
                'product_id': service.id,
                'product_uom': service_tmpl.uom_po_id.id,
                'price_unit': (service_supplier_infos[0].price
                               if service_supplier_infos
                               else 0.0),
                'company_id': self.env.user.company_id.id,
                'date_planned': str(datetime.now())
                })]
            })
