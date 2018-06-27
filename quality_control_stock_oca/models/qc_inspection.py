# -*- coding: utf-8 -*-
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.multi
    @api.depends('object_id')
    def _compute_picking(self):
        for inspection in self:
            inspection.picking = False
            if inspection.object_id:
                if inspection.object_id._name == 'stock.move':
                    inspection.picking = inspection.object_id.picking_id
                elif inspection.object_id._name == 'stock.picking':
                    inspection.picking = inspection.object_id
                elif inspection.object_id._name == 'stock.pack.operation':
                    inspection.picking = inspection.object_id.picking_id

    @api.multi
    @api.depends('object_id')
    def _compute_lot(self):
        for inspection in self:
            inspection.lot = False
            if inspection.object_id:
                if inspection.object_id._name == 'stock.pack.operation':
                    inspection.lot = \
                        inspection.object_id.pack_lot_ids[:1].lot_id
                elif inspection.object_id._name == 'stock.move':
                    inspection.lot = inspection.object_id.lot_ids[:1]
                elif inspection.object_id._name == 'stock.production.lot':
                    inspection.lot = inspection.object_id

    @api.multi
    @api.depends('object_id')
    def _get_product(self):
        """Overriden for getting the product from a stock move."""
        self.ensure_one()
        super(QcInspection, self)._get_product()
        if self.object_id:
            if self.object_id._name == 'stock.move':
                self.product = self.object_id.product_id
            elif self.object_id._name == 'stock.pack.operation':
                self.product = self.object_id.product_id
            elif self.object_id._name == 'stock.production.lot':
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
        if object_ref and object_ref._name == 'stock.move':
            res['qty'] = object_ref.product_uom_qty
        return res

    picking = fields.Many2one(
        comodel_name="stock.picking", compute="_compute_picking", store=True)
    lot = fields.Many2one(
        comodel_name='stock.production.lot', compute="_compute_lot",
        store=True)


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    picking = fields.Many2one(
        comodel_name="stock.picking", related="inspection_id.picking",
        store=True)
    lot = fields.Many2one(
        comodel_name="stock.production.lot", related="inspection_id.lot",
        store=True)
