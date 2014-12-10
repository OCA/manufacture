# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    force_valid = fields.Boolean(
        string='Force valid',
        help="Mark this field if you want to override the result of the "
             "inspection")

    @api.multi
    def action_confirm(self):
        res = super(QcInspection, self).action_confirm()
        for inspection in self:
            if inspection.force_valid and inspection.state != 'success':
                inspection.state = 'success'
        return res

    @api.multi
    def action_approve(self):
        res = super(QcInspection, self).action_approve()
        for inspection in self:
            if inspection.force_valid and inspection.state != 'success':
                inspection.state = 'success'
        return res
