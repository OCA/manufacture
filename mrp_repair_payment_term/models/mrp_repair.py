# -*- coding: utf-8 -*-
# Copyright 2016 Nicola Malcontenti
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields
from openerp.osv import osv


class MRPRepair(models.Model):
    _inherit = "mrp.repair"

    payment_term = fields.Many2one(
        'account.payment.term',
        string='Payment Term'
    )


class mrp_repair(osv.osv):
    _inherit = 'mrp.repair'

    def onchange_partner_id(self, cr, uid, ids, part, address_id):
        res = super(mrp_repair, self).onchange_partner_id(
            cr, uid, ids, part, address_id)
        part_obj = self.pool.get('res.partner')
        if not part:
            res['value']['payment_term'] = False
        else:
            partner = part_obj.browse(cr, uid, part)
            if partner.property_payment_term:
                res['value']['payment_term'] = partner.property_payment_term.id
            else:
                res['value']['payment_term'] = False
        return res

    def action_invoice_create(self, cr, uid, ids, group=False, context=None):
        res = super(mrp_repair, self).action_invoice_create(
            cr, uid, ids, group, context)
        for inv_id in res:
            if res[inv_id]:
                payment_term = self.browse(cr, uid, ids).payment_term.id
                if payment_term:
                    self.pool.get('account.invoice').write(
                        cr, uid, res[inv_id], {
                            'payment_term': payment_term}, context)
        return res
