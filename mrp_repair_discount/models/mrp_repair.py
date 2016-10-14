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
