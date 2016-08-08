# -*- coding: utf-8 -*-
# Copyright 2014 Pedro M. Baeza (http://www.tecnativa.com)
# Copyright 2014 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
