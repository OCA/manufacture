# -*- coding: utf-8 -*-
# © 2015 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
from openerp.osv import orm


class MrpRepairLine(models.Model):
    _inherit = 'mrp.repair.line'

    discount = fields.Float(string='Discount (%)')


class MrpRepair(orm.Model):
    _inherit = 'mrp.repair'

    def action_invoice_create(self, cr, uid, ids, group=False, context=None):
        res = super(MrpRepair, self).action_invoice_create(
            cr, uid, ids, group, context)
        repair_obj = self.browse(cr, uid, ids, context=context)
        for op in repair_obj.operations:
            op.invoice_line_id.discount = op.discount
        return res
