# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RepairOrder(models.Model):

    _inherit = 'repair.order'

    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Payment Term',
    )

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.partner_id:
            self.payment_term_id = self.partner_id.with_context(
                force_company=self.company_id.id
            ).property_payment_term_id
        else:
            self.payment_term_id = False
        return res

    @api.multi
    def action_invoice_create(self, group=False):
        res = super().action_invoice_create(group)
        for record in self:
            if record.invoice_id and record.payment_term_id:
                record.invoice_id.payment_term_id = record.payment_term_id
        return res
