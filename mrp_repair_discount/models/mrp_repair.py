# -*- coding: utf-8 -*-
# © 2015 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class MrpRepairLine(orm.Model):
    _inherit = 'mrp.repair.line'

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = super(MrpRepairLine, self)._amount_line(
            cr, uid, ids, field_name, arg, context=None)
        for line in self.browse(cr, uid, ids, context=context):
            price = res[line.id] * (1 - (line.discount or 0.0) / 100.0)
            res[line.id] = price
        return res

    _columns = {
        'discount': fields.float(string='Discount (%)'),
        'price_subtotal': fields.function(
            _amount_line, string='Subtotal',
            digits_compute=dp.get_precision('Account')),

    }


class MrpRepair(orm.Model):
    _inherit = 'mrp.repair'

    def action_invoice_create(self, cr, uid, ids, group=False, context=None):
        res = super(MrpRepair, self).action_invoice_create(
            cr, uid, ids, group, context)
        repair = self.browse(cr, uid, ids, context=context)
        for op in repair.operations:
            if op.to_invoice:
                op.invoice_line_id.discount = op.discount
        repair.invoice_id.button_reset_taxes()
        return res
