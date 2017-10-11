# -*- coding: utf-8 -*-
# Copyright 2015 Nicola Malcontenti - Agile Business Group
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import openerp.addons.decimal_precision as dp


class RepairFee(models.Model):
    _inherit = 'mrp.repair.fee'

    @api.one
    @api.depends(
        'to_invoice',
        'price_unit',
        'repair_id',
        'product_uom_qty',
        'product_id')
    def _compute_price_subtotal(self):
        if not self.to_invoice:
            self.price_subtotal = 0.0
        else:
            taxes = self.env['account.tax'].compute_all(
                self.price_unit, self.repair_id.pricelist_id.currency_id,
                self.product_uom_qty, self.product_id,
                self.repair_id.partner_id)
            self.price_subtotal = (
                taxes['total_excluded'] * (1 - (self.discount or 0.0) / 100.0))

    discount = fields.Float(string='Discount (%)')
    price_subtotal = fields.Float(
        'Subtotal',
        compute='_compute_price_subtotal',
        digits=dp.get_precision('Account'))


class MrpRepairLine(models.Model):
    _inherit = 'mrp.repair.line'

    @api.one
    @api.depends(
        'to_invoice',
        'price_unit',
        'repair_id',
        'product_uom_qty',
        'product_id')
    def _compute_price_subtotal(self):
        if not self.to_invoice:
            self.price_subtotal = 0.0
        else:
            taxes = self.env['account.tax'].compute_all(
                self.price_unit, self.repair_id.pricelist_id.currency_id,
                self.product_uom_qty, self.product_id,
                self.repair_id.partner_id)
            self.price_subtotal = (
                taxes['total_excluded'] * (1 - (self.discount or 0.0) / 100.0))

    discount = fields.Float(string='Discount (%)')
    price_subtotal = fields.Float(
        'Subtotal',
        compute='_compute_price_subtotal',
        digits=dp.get_precision('Account'))


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    @api.multi
    def action_invoice_create(self, group=False):
        res = super(MrpRepair, self).action_invoice_create(group)
        for repair in self:
            operations = repair.operations.filtered('to_invoice')
            fees_lines = repair.fees_lines.filtered('to_invoice')
            if repair.invoice_method != 'none':
                for op in operations:
                    op.invoice_line_id.discount = op.discount
                if operations:
                    repair.invoice_id.compute_taxes()
                for fl in fees_lines:
                    fl.invoice_line_id.discount = fl.discount
                if fees_lines:
                    repair.invoice_id.compute_taxes()
        return res

    def _calc_line_base_price(self, line):
        return line.price_unit * (1 - (line.discount or 0.0) / 100.0)

    @api.multi
    @api.depends('operations', 'fees_lines')
    def _compute_tax(self):
        for repair in self:
            val = 0.0
            cur = repair.pricelist_id.currency_id
            for line in repair.operations:
                if line.to_invoice:
                    tax_calculate = line.tax_id.compute_all(
                        self._calc_line_base_price(line),
                        self.pricelist_id.currency_id,
                        line.product_uom_qty,
                        line.product_id,
                        repair.partner_id)
                    for c in tax_calculate['taxes']:
                        val += c['amount']
            for line in repair.fees_lines:
                if line.to_invoice:
                    tax_calculate = line.tax_id.compute_all(
                        self._calc_line_base_price(line),
                        self.pricelist_id.currency_id,
                        line.product_uom_qty,
                        line.product_id,
                        repair.partner_id)
                    for c in tax_calculate['taxes']:
                        val += c['amount']
            repair.amount_tax = cur.round(val)

    amount_tax = fields.Float(
        string='Taxes', compute='_compute_tax')
