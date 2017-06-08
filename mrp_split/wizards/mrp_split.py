# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class MrpSplit(models.TransientModel):
    _name = "mrp.split"
    _description = "Wizard to split MOs."

    @api.multi
    def compute_product_line_ids(self):
        self.product_line_ids.unlink()
        self.production_id.action_compute()
        for pl in self.production_id.product_lines:
            vals = self._prepare_product_line(pl)
            self.env['mrp.split.product.line'].create(vals)
        self._get_split_qty()
        return {"type": "ir.actions.do_nothing"}

    @api.one
    def _get_split_qty(self):
        """Propose a split qty to split the MO into two with one totally
        available to produce."""
        bottle_neck = min(self.product_line_ids.mapped('bottle_neck_factor'))
        bottle_neck = max(min(1, bottle_neck), 0)
        self.split_qty = self.production_qty * bottle_neck

    production_id = fields.Many2one(
        comodel_name='mrp.production', string='Manufacturing Order',
        readonly=True)
    production_qty = fields.Float(
        related='production_id.product_qty', readonly=True,
        string="Original Quantity")
    bom_id = fields.Many2one(related='production_id.bom_id', readonly=True)
    product_line_ids = fields.One2many(
        comodel_name='mrp.split.product.line', string='Products needed',
        inverse_name='mrp_split_id', readonly=True)
    split_qty = fields.Float(
        string='Quantity to split')

    def _prepare_product_line(self, pl):
        return {
            'product_id': pl.product_id.id,
            'product_qty': pl.product_qty,
            'product_uom': pl.product_uom.id,
            'mrp_split_id': self.id,
            'location_id': self.production_id.location_src_id.id,
        }

    @api.multi
    def do_split(self):
        # TODO: add constrains
        res = self._do_split()
        return res

    @api.multi
    def _do_split(self):
        self.ensure_one()
        original_qty = self.production_id.product_qty
        self.production_id.write({'product_qty': self.split_qty})
        self.production_id.action_compute()
        if self.production_id.state == 'confirmed':
            # Cancel moves related to product to consume to propagate to the
            # procurement (in case we use module mrp_mto_with_stock.
            self.production_id.move_lines.action_cancel()
            # Delete moves related to products to produce to not propagete
            # the cancel to pickings.
            self.production_id.move_created_ids.write({'state': 'draft'})
            self.production_id.move_created_ids.unlink()
            self.production_id.product_lines.unlink()
            self.production_id.with_context(
                default_production_id=False).action_confirm()
        backorder = self.production_id.copy()
        backorder.write({
            'product_qty': original_qty - self.split_qty,
            'backorder_id': self.production_id.id,
            'move_prod_id': self.production_id.move_prod_id.id,
        })
        if self.production_id.state == 'confirmed':
            # If originating MO was confirmed confirm the new on to ensure
            # that move_prod_id is still fulfilled with the whole original qty.
            backorder.action_confirm()
        # Open resulting MOs
        ids = [self.production_id.id, backorder.id]
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        action.update({'domain': [('id', 'in', ids)]})
        return action


class MrpSplitLine(models.TransientModel):
    _name = "mrp.split.product.line"

    @api.one
    def _compute_available_qty(self):
        product_available = self.product_id.with_context(
            location=self.location_id.id)._product_available()[
            self.product_id.id]['qty_available_not_res']
        res = self.product_uom._compute_qty(
            self.product_id.product_tmpl_id.uom_id.id, product_available,
            self.product_uom.id)
        self.available_qty = res

    @api.one
    def _compute_bottle_neck_factor(self):
        if self.product_qty:
            self.bottle_neck_factor = self.available_qty / self.product_qty

    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    product_qty = fields.Float(
        string='Quantity Required', required=True,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uom = fields.Many2one(
        comodel_name='product.uom', string='UoM', required=True)
    mrp_split_id = fields.Many2one(comodel_name='mrp.split')
    available_qty = fields.Float(
        string='Quantity Available', compute=_compute_available_qty,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    bottle_neck_factor = fields.Float(compute=_compute_bottle_neck_factor)
    location_id = fields.Many2one(comodel_name='stock.location', required=True)
