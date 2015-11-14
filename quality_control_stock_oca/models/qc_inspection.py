# -*- coding: utf-8 -*-
# (c) 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

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
                self.lot = self.object_id.lot_ids[:1]

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

    @api.onchange('object_id')
    def onchange_object_id(self):
        if self.object_id:
            if self.object_id._name == 'stock.move':
                self.qty = self.object_id.product_qty
            elif self.object_id._name == 'stock.pack.operation':
                self.qty = self.object_id.product_qty

    @api.multi
    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super(QcInspection, self)._prepare_inspection_header(
            object_ref, trigger_line)
        # Fill qty when coming from pack operations
        if object_ref and object_ref._name == 'stock.pack.operation':
            res['qty'] = object_ref.product_qty
        return res

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
