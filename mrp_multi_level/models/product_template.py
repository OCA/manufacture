# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mrp_applicable = fields.Boolean(string='MRP Applicable',
                                    compute='_compute_mrp_applicable',
                                    inverse='_set_mrp_applicable', store=True
                                    )
    mrp_exclude = fields.Boolean(string='Exclude from MRP',
                                 compute='_compute_mrp_exclude',
                                 inverse='_set_mrp_exclude', store=True
                                 )
    mrp_inspection_delay = fields.Integer(
        string='Inspection Delay',
        compute='_compute_mrp_inspection_delay',
        inverse='_set_mrp_inspection_delay',
        store=True
    )
    mrp_maximum_order_qty = fields.Float(
        string='Maximum Order Qty',
        compute='_compute_mrp_maximum_order_qty',
        inverse='_set_mrp_maximum_order_qty', store=True
    )
    mrp_minimum_order_qty = fields.Float(
        string='Minimum Order Qty',
        compute='_compute_mrp_minimum_order_qty',
        inverse='_set_mrp_minimum_order_qty', store=True
    )
    mrp_minimum_stock = fields.Float(
        string='Minimum Stock',
        compute='_compute_mrp_minimum_stock',
        inverse='_set_mrp_minimum_stock', store=True
    )
    mrp_nbr_days = fields.Integer(
        string='Nbr. Days',
        compute='_compute_mrp_nbr_days',
        inverse='_set_mrp_nbr_days', store=True,
        help="Number of days to group demand for this product during the "
             "MRP run, in order to determine the quantity to order.",
    )
    mrp_qty_multiple = fields.Float(
        string='Qty Multiple', default=1.00,
        compute='_compute_mrp_qty_multiple',
        inverse='_set_mrp_qty_multiple', store=True
    )
    mrp_transit_delay = fields.Integer(
        string='Transit Delay', default=0,
        compute='_compute_mrp_transit_delay',
        inverse='_set_mrp_transit_delay', store=True
    )
    mrp_verified = fields.Boolean(
        string='Verified for MRP',
        compute='_compute_mrp_verified',
        inverse='_set_mrp_verified', store=True,
        help="Identifies that this product has been verified "
             "to be valid for the MRP.",
    )

    @api.depends('product_variant_ids', 'product_variant_ids.mrp_applicable')
    def _compute_mrp_applicable(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.mrp_applicable = \
                template.product_variant_ids.mrp_applicable
        for template in (self - unique_variants):
            template.mrp_applicable = False

    @api.one
    def _set_mrp_applicable(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.mrp_applicable = self.mrp_applicable

    @api.depends('product_variant_ids', 'product_variant_ids.mrp_exclude')
    def _compute_mrp_exclude(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.mrp_exclude = \
                template.product_variant_ids.mrp_exclude
        for template in (self - unique_variants):
            template.mrp_exclude = False

    @api.one
    def _set_mrp_exclude(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.mrp_exclude = self.mrp_exclude

    @api.depends('product_variant_ids',
                 'product_variant_ids.mrp_inspection_delay')
    def _compute_mrp_inspection_delay(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.mrp_inspection_delay = \
                template.product_variant_ids.mrp_inspection_delay
        for template in (self - unique_variants):
            template.mrp_inspection_delay = 0

    @api.one
    def _set_mrp_inspection_delay(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.mrp_inspection_delay = \
                self.mrp_inspection_delay

    @api.depends('product_variant_ids',
                 'product_variant_ids.mrp_maximum_order_qty')
    def _compute_mrp_maximum_order_qty(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.mrp_maximum_order_qty = \
                template.product_variant_ids.mrp_maximum_order_qty
        for template in (self - unique_variants):
            template.mrp_maximum_order_qty = 0.0

    @api.one
    def _set_mrp_maximum_order_qty(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.mrp_maximum_order_qty = \
                self.mrp_maximum_order_qty

    @api.depends('product_variant_ids',
                 'product_variant_ids.mrp_minimum_order_qty')
    def _compute_mrp_minimum_order_qty(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.mrp_minimum_order_qty = \
                template.product_variant_ids.mrp_minimum_order_qty
        for template in (self - unique_variants):
            template.mrp_minimum_order_qty = 0.0

    @api.one
    def _set_mrp_minimum_order_qty(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.mrp_minimum_order_qty = \
                self.mrp_minimum_order_qty

    @api.depends('product_variant_ids',
                 'product_variant_ids.mrp_minimum_stock')
    def _compute_mrp_minimum_stock(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.mrp_minimum_stock = \
                template.product_variant_ids.mrp_minimum_stock
        for template in (self - unique_variants):
            template.mrp_minimum_stock = 0.0

    @api.one
    def _set_mrp_minimum_stock(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.mrp_minimum_stock = \
                self.mrp_minimum_stock

    @api.depends('product_variant_ids',
                 'product_variant_ids.mrp_nbr_days')
    def _compute_mrp_nbr_days(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.mrp_nbr_days = \
                template.product_variant_ids.mrp_nbr_days
        for template in (self - unique_variants):
            template.mrp_nbr_days = 0.0

    @api.one
    def _set_mrp_nbr_days(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.mrp_nbr_days = \
                self.mrp_nbr_days

    @api.depends('product_variant_ids',
                 'product_variant_ids.mrp_qty_multiple')
    def _compute_mrp_qty_multiple(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.mrp_qty_multiple = \
                template.product_variant_ids.mrp_qty_multiple
        for template in (self - unique_variants):
            template.mrp_qty_multiple = 1

    @api.one
    def _set_mrp_qty_multiple(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.mrp_qty_multiple = \
                self.mrp_qty_multiple

    @api.depends('product_variant_ids',
                 'product_variant_ids.mrp_transit_delay')
    def _compute_mrp_transit_delay(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.mrp_transit_delay = \
                template.product_variant_ids.mrp_transit_delay
        for template in (self - unique_variants):
            template.mrp_transit_delay = 0.0

    @api.one
    def _set_mrp_transit_delay(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.mrp_transit_delay = \
                self.mrp_transit_delay

    @api.depends('product_variant_ids',
                 'product_variant_ids.mrp_verified')
    def _compute_mrp_verified(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.mrp_verified = \
                template.product_variant_ids.mrp_verified
        for template in (self - unique_variants):
            template.mrp_verified = 0.0

    @api.one
    def _set_mrp_verified(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.mrp_verified = \
                self.mrp_verified
