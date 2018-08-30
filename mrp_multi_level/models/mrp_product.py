# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from math import ceil

from odoo import api, fields, models


class MrpProduct(models.Model):
    _name = 'mrp.product'

    mrp_area_id = fields.Many2one(
        comodel_name='mrp.area', string='MRP Area',
    )
    current_qty_available = fields.Float(
        string='Current Qty Available',
        related='product_id.qty_available',
    )
    main_supplier_id = fields.Many2one(
        comodel_name='res.partner', string='Main Supplier',
        compute='_compute_main_supplier', store=True,
        index=True,
    )
    main_supplierinfo_id = fields.Many2one(
        comodel_name='product.supplierinfo', string='Supplier Info',
        compute='_compute_main_supplier', store=True,
    )
    mrp_inspection_delay = fields.Integer(
        string='Inspection Delay',
        related='product_id.mrp_inspection_delay')
    mrp_lead_time = fields.Float(
        string='Lead Time',
        related='product_id.produce_delay',
    )
    mrp_llc = fields.Integer(
        string='Low Level Code', index=True, readonly=True,
    )
    # TODO: minimun stock and max/min order qty assigned by area?
    mrp_maximum_order_qty = fields.Float(
        string='Maximum Order Qty',
        related='product_id.mrp_maximum_order_qty',
    )
    mrp_minimum_order_qty = fields.Float(
        string='Minimum Order Qty',
        related='product_id.mrp_minimum_order_qty',
    )
    mrp_minimum_stock = fields.Float(
        string='Minimum Stock',
        related='product_id.mrp_minimum_stock',
    )
    mrp_move_ids = fields.One2many(
        comodel_name='mrp.move', inverse_name='mrp_product_id',
        string='MRP Moves',
    )
    mrp_nbr_days = fields.Integer(
        string='Nbr. Days', related='product_id.mrp_nbr_days')
    mrp_qty_available = fields.Float(
        string='MRP Qty Available')
    mrp_qty_multiple = fields.Float(
        string='Qty Multiple',
        related='product_id.mrp_qty_multiple',
    )
    mrp_transit_delay = fields.Integer(related='product_id.mrp_transit_delay')
    mrp_verified = fields.Boolean(
        string='MRP Verified',
        related='product_id.mrp_verified',
    )
    name = fields.Char(string='Description')
    # TODO: rename to mrp_action_count?
    nbr_mrp_actions = fields.Integer(
        string='Nbr Actions', index=True,
    )
    nbr_mrp_actions_4w = fields.Integer(
        string='Nbr Actions 4 Weeks', index=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product',
        index=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        related='product_id.product_tmpl_id',
    )
    supply_method = fields.Selection(
        selection=[('buy', 'Buy'),
                   ('none', 'Undefined'),
                   ('manufacture', 'Produce'),
                   ('move', 'Transfer')],
        string='Supply Method',
        compute='_compute_supply_method', store=True,
    )

    @api.multi
    @api.depends('mrp_area_id')
    def _compute_supply_method(self):
        group_obj = self.env['procurement.group']
        for rec in self:
            values = {
                'warehouse_id': rec.mrp_area_id.warehouse_id,
                'company_id': self.env.user.company_id.id,
                # TODO: better way to get company
            }
            rule = group_obj._get_rule(
                rec.product_id, rec.mrp_area_id.location_id, values)
            rec.supply_method = rule.action if rule else 'none'

    @api.multi
    @api.depends('supply_method')
    def _compute_main_supplier(self):
        """Simplified and similar to procurement.rule logic."""
        for rec in self.filtered(lambda r: r.supply_method == 'buy'):
            suppliers = rec.product_id.seller_ids.filtered(
                lambda r: (not r.product_id or r.product_id == rec.product_id))
            if not suppliers:
                continue
            rec.main_supplierinfo_id = suppliers[0]
            rec.main_supplier_id = suppliers[0].name

    @api.multi
    def _adjust_qty_to_order(self, qty_to_order):
        self.ensure_one()
        if (not self.mrp_maximum_order_qty and not
                self.mrp_minimum_order_qty and self.mrp_qty_multiple == 1.0):
            return qty_to_order
        if qty_to_order < self.mrp_minimum_order_qty:
            return self.mrp_minimum_order_qty
        if self.mrp_qty_multiple:
            multiplier = ceil(qty_to_order / self.mrp_qty_multiple)
            qty_to_order = multiplier * self.mrp_qty_multiple
        if self.mrp_maximum_order_qty and qty_to_order > \
                self.mrp_maximum_order_qty:
            return self.mrp_maximum_order_qty
        return qty_to_order
