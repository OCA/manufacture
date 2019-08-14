# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.onchange('object_id')
    def onchange_object_id(self):
        if self.object_id:
            if self.object_id._name == 'stock.move':
                self.qty = self.object_id.product_qty
            elif self.object_id._name == 'stock.move.line':
                self.qty = self.object_id.product_qty

    @api.multi
    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super(QcInspection, self)._prepare_inspection_header(
            object_ref, trigger_line)
        # Fill qty when coming from pack operations
        if object_ref:
            if object_ref._name == 'stock.move.line':
                res['qty'] = object_ref.product_qty
            elif object_ref._name == 'stock.move':
                res['qty'] = object_ref.product_uom_qty
        return res

    picking_id = fields.Many2one(
        comodel_name="stock.picking", compute="_compute_values", store=True)
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot', compute="_compute_values",
        store=True)

    def _get_values_by_object(self):
        res = super(QcInspection, self)._get_values_by_object()
        with_object = self.search([
            ('id', 'in', self.ids),
            ('object_id', '!=', False),
        ])
        for inspection in with_object:
            obj = inspection.object_id
            if obj._name == 'stock.picking':
                res[inspection].update({
                    'picking_id': obj.id,
                    'lot_id': False,
                })
            elif obj._name == 'stock.production.lot':
                res[inspection].update({
                    'picking_id': False,
                    'product_id': obj.product_id.id,
                    'lot_id': obj.id,
                })
            elif obj._name == 'stock.move.line':
                res[inspection].update({
                    'picking_id': obj.picking_id.id,
                    'product_id': obj.product_id.id,
                    'lot_id': obj.lot_id.id,
                })
            elif obj._name == 'stock.move':
                lot = self.env['stock.move.line'].search([
                    ('lot_id', '!=', False),
                    ('move_id', '=', obj.id),
                ], limit=1).lot_id
                res[inspection].update({
                    'picking_id': obj.picking_id.id,
                    'product_id': obj.product_id.id,
                    'lot_id': lot.id,
                })
            else:
                res[inspection].update({
                    'picking_id': False,
                    'lot_id': False,
                })
        return res


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    picking_id = fields.Many2one(
        comodel_name="stock.picking", related="inspection_id.picking_id",
        store=True)
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot", related="inspection_id.lot_id",
        store=True)
