# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.one
    @api.depends('object_id')
    def get_picking(self):
        self.picking = False
        if self.object_id:
            if self.object_id._name == 'stock.move':
                self.picking = self.object_id.picking_id
            elif self.object_id._name == 'stock.picking':
                self.picking = self.object_id
            elif self.object_id._name == 'stock.pack.operation':
                self.picking = self.object_id.picking_id

    @api.one
    @api.depends('object_id')
    def get_lot(self):
        self.lot = False
        if self.object_id:
            if self.object_id._name == 'stock.pack.operation':
                self.lot = self.object_id.lot_id
            elif self.object_id._name == 'stock.move':
                if self.object_id.lot_ids:
                    self.lot = self.object_id.lot_ids[0]

    @api.one
    @api.depends('object_id')
    def _get_product(self):
        """Overriden for getting the product from a stock move."""
        super(QcInspection, self)._get_product()
        if self.object_id:
            if self.object_id._name == 'stock.move':
                self.product = self.object_id.product_id
            elif self.object_id._name == 'stock.pack.operation':
                self.product = self.object_id.product_id

    @api.one
    @api.depends('object_id')
    def _get_qty(self):
        super(QcInspection, self)._get_qty()
        if self.object_id:
            if self.object_id._name == 'stock.move':
                self.qty = self.object_id.product_qty
            elif self.object_id._name == 'stock.pack.operation':
                self.qty = self.object_id.product_qty

    picking = fields.Many2one(
        comodel_name="stock.picking", compute="get_picking", store=True)
    lot = fields.Many2one(
        comodel_name='stock.production.lot', compute="get_lot", store=True)


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    picking = fields.Many2one(
        comodel_name="stock.picking", related="inspection_id.picking",
        store=True)
    lot = fields.Many2one(
        comodel_name="stock.production.lot", related="inspection_id.lot",
        store=True)
