# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    active_draft = fields.Boolean(
        string='Keep re-editing BoM active',
        help='This will allow you to define if those BoM passed back to draft'
        ' are still activated or not', default=False)
