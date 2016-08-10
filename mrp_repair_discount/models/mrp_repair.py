# -*- coding: utf-8 -*-
# © 2015 Nicola Malcontenti - Agile Business Group
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.osv import fields as old_fields
import openerp.addons.decimal_precision as dp


class MrpRepairLine(models.Model):
    _inherit = 'mrp.repair.line'

    discount = fields.Float(string='Discount (%)')

    @api.multi
    def _amount_line(self, field_name, arg):
        res = super(MrpRepairLine, self)._amount_line(field_name, arg)
        for line in self.filtered('discount'):
            price = res[line.id] * (1 - (line.discount or 0.0) / 100.0)
            res[line.id] = price
        return res

    _columns = {
        # Must be defined in old API so that we can call super in the compute
        'price_subtotal': old_fields.function(
            _amount_line, string='Subtotal',
            digits_compute=dp.get_precision('Account')),
    }


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    @api.multi
    def action_invoice_create(self, group=False):
        res = super(MrpRepair, self).action_invoice_create(group)
        for repair in self:
            operations = repair.operations.filtered('to_invoice')
            for op in operations:
                op.invoice_line_id.discount = op.discount
            if operations:
                repair.invoice_id.button_reset_taxes()
        return res

    def _calc_line_base_price(self, line):
        return line.price_unit * (1 - (line.discount or 0.0) / 100.0)

    def _get_lines(self, cr, uid, ids, context=None):
        return self.pool['mrp.repair'].search(
            cr, uid, [('operations', 'in', ids)], context=context)

    def _get_fee_lines(self, cr, uid, ids, context=None):
        return self.pool['mrp.repair'].search(
            cr, uid, [('fees_lines', 'in', ids)], context=context)

    def _amount_tax(self, cr, uid, ids, field_name, arg, context=None):
        # Can't call super because we have to call compute_all with different
        # parameter for each line and compute the total amount
        res = {}
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for repair in self.browse(cr, uid, ids, context=context):
            val = 0.0
            cur = repair.pricelist_id.currency_id
            for line in repair.operations:
                if line.to_invoice:
                    tax_calculate = tax_obj.compute_all(
                        cr, uid, line.tax_id, self._calc_line_base_price(line),
                        line.product_uom_qty, line.product_id,
                        repair.partner_id)
                    for c in tax_calculate['taxes']:
                        val += c['amount']
            for line in repair.fees_lines:
                if line.to_invoice:
                    tax_calculate = tax_obj.compute_all(
                        cr, uid, line.tax_id, line.price_unit,
                        line.product_uom_qty, line.product_id,
                        repair.partner_id)
                    for c in tax_calculate['taxes']:
                        val += c['amount']
            res[repair.id] = cur_obj.round(cr, uid, cur, val)
        return res

    _columns = {
        'amount_tax': old_fields.function(
            _amount_tax, string='Taxes',
            store={
                'mrp.repair': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['operations', 'fees_lines'], 10),
                'mrp.repair.line': (
                    _get_lines, [
                        'price_unit', 'price_subtotal', 'product_id', 'tax_id',
                        'product_uom_qty', 'product_uom', 'discount',
                    ], 10),
                'mrp.repair.fee': (
                    _get_fee_lines, [
                        'price_unit', 'price_subtotal', 'product_id', 'tax_id',
                        'product_uom_qty', 'product_uom'
                    ], 10),
            }),
    }
