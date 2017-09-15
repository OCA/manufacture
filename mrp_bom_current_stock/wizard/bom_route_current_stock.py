# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class BomRouteCurrentStock(models.TransientModel):
    _name = "mrp.bom.current.stock"

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.bom_id = self.env['mrp.bom']._bom_find(
            product_id=self.product_id.id, properties=[])

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        if self.bom_id.location_id:
            self.location_id = self.bom_id.location_id

    bom_id = fields.Many2one(
        comodel_name="mrp.bom", string="Starting Bill of Materials",
        required=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product Variant',
        domain="[('type', 'in', ['product', 'consu'])]", required=True)
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string='Product Template',
        related='product_id.product_tmpl_id')
    product_qty = fields.Float(
        related='bom_id.product_qty',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one(
        comodel_name="product.uom", related="bom_id.product_uom")
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Starting location")
    line_ids = fields.One2many(
        comodel_name='mrp.bom.current.stock.line',
        inverse_name='explosion_id')

    @api.model
    def _prepare_line(self, bom_line, level, factor):
        return {
            'product_id': bom_line.product_id.id,
            'bom_line': bom_line.id,
            'bom_level': level,
            'product_qty': bom_line.product_qty * factor,
            'product_uom_id': bom_line.product_uom.id,
            'location_id': (bom_line.location_id.id if bom_line.location_id
                            else False),
            'explosion_id': self.id,
        }

    @api.multi
    def do_explode(self):
        self.ensure_one()
        line_obj = self.env['mrp.bom.current.stock.line']

        def _create_lines(bom, level=0, factor=1):
            level += 1
            for line in bom.bom_line_ids:
                vals = self._prepare_line(line, level, factor)
                line_obj.create(vals)
                location = line.location_id
                line_boms = line.product_id.bom_ids
                bom = line_boms.filtered(
                    lambda bom: bom.location_id == location) or \
                    line_boms.filtered(lambda b: not b.location_id)
                if bom:
                    line_qty = self.env['product.uom']._compute_qty_obj(
                        line.product_uom, line.product_qty, bom.product_uom)
                    new_factor = factor * line_qty / bom.product_qty
                    _create_lines(bom[0], level, new_factor)
        _create_lines(self.bom_id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Open lines',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'mrp.bom.current.stock',
            'view_id': self.env.ref(
                'mrp_bom_current_stock.'
                'mrp_bom_current_stock_view_form2').id,
            'target': 'new',
            'res_id': self.id,
        }


class BomRouteCurrentStockLine(models.TransientModel):
    _name = "mrp.bom.current.stock.line"

    @api.one
    def _compute_qty_available_in_source_loc(self):
        product_available = self.product_id.with_context(
            location=self.location_id.id)._product_available()[
            self.product_id.id]['qty_available']
        res = self.product_uom_id._compute_qty(
            self.product_id.product_tmpl_id.uom_id.id, product_available,
            self.product_uom_id.id)
        self.qty_available_in_source_loc = res

    explosion_id = fields.Many2one(
        comodel_name='mrp.bom.current.stock')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product Variant',
        readonly=True)
    bom_level = fields.Integer(string='BoM Level', readonly=True)
    product_qty = fields.Float(
        string='Product Quantity', readonly=True,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one(
        comodel_name='product.uom', string='Product Unit of Measure',
        readonly=True)
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Source location")
    bom_line = fields.Many2one(
        comodel_name="mrp.bom.line", string="BoM line")
    qty_available_in_source_loc = fields.Float(
        string="Qty Available in Source",
        compute=_compute_qty_available_in_source_loc)
