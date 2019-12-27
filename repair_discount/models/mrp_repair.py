# Copyright 2015 Nicola Malcontenti - Agile Business Group
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class RepairFee(models.Model):
    _inherit = 'repair.fee'

    @api.depends(
        'invoiced',
        'price_unit',
        'repair_id',
        'product_uom_qty',
        'product_id')
    def _compute_price_subtotal(self):
        for record in self:
            taxes = self.env['account.tax'].compute_all(
                record.price_unit, record.repair_id.pricelist_id.currency_id,
                record.product_uom_qty, record.product_id,
                record.repair_id.partner_id
            )

            record.price_subtotal = (
                taxes['total_excluded'] * (1 - (record.discount or 0.0) / 100.0)
            )

    discount = fields.Float(string='Discount (%)')
    price_subtotal = fields.Float(
        'Subtotal',
        compute='_compute_price_subtotal',
        digits=dp.get_precision('Account'))


class RepairLine(models.Model):
    _inherit = 'repair.line'

    @api.depends(
        'invoiced',
        'price_unit',
        'repair_id',
        'product_uom_qty',
        'product_id')
    def _compute_price_subtotal(self):
        for repair_line in self:
            taxes = self.env['account.tax'].compute_all(
                repair_line.price_unit,
                repair_line.repair_id.pricelist_id.currency_id,
                repair_line.product_uom_qty, repair_line.product_id,
                repair_line.repair_id.partner_id
            )
            repair_line.price_subtotal = (
                taxes['total_excluded'] * (1 - (repair_line.discount or 0.0) / 100.0)
            )

    discount = fields.Float(string='Discount (%)')
    price_subtotal = fields.Float(
        'Subtotal',
        compute='_compute_price_subtotal',
        digits=dp.get_precision('Account'))


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    @api.multi
    def action_invoice_create(self, group=False):
        res = super(RepairOrder, self).action_invoice_create(group)
        for repair in self.filtered(
            lambda _repair: _repair.invoice_method != 'none'
        ):
            operations = repair.operations
            fees_lines = repair.fees_lines

            for op in operations.filtered(
                lambda item: item.invoice_line_id
            ):
                op.invoice_line_id.discount = op.discount
            if operations:
                repair.invoice_id.compute_taxes()

            for fee_lines in fees_lines.filtered(
                lambda item: item.invoice_line_id
            ):
                fee_lines.invoice_line_id.discount = fee_lines.discount
            if fees_lines:
                repair.invoice_id.compute_taxes()

        return res

    def _calculate_line_base_price(self, line):
        return line.price_unit * (1 - (line.discount or 0.0) / 100.0)

    @api.depends('operations', 'fees_lines', 'operations.invoiced',
                 'fees_lines.invoiced')
    def _amount_tax(self):
        for repair in self:
            taxed_amount = 0.0
            currency = repair.pricelist_id.currency_id

            for line in repair.operations:
                tax_calculate = line.tax_id.compute_all(
                    self._calculate_line_base_price(line),
                    self.pricelist_id.currency_id,
                    line.product_uom_qty,
                    line.product_id,
                    repair.partner_id
                )

                for c in tax_calculate['taxes']:
                    taxed_amount += c['amount']

            for line in repair.fees_lines:
                tax_calculate = line.tax_id.compute_all(
                    self._calculate_line_base_price(line),
                    self.pricelist_id.currency_id,
                    line.product_uom_qty,
                    line.product_id,
                    repair.partner_id)
                for c in tax_calculate['taxes']:
                    taxed_amount += c['amount']

            repair.amount_tax = currency.round(taxed_amount)
