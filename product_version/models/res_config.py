# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    group_product_version = fields.Boolean(
        string='Allow to re-edit Products',
        implied_group='mrp_product_version.group_product_version',
        help='The active state may be passed back to state draft')
    active_product_draft = fields.Boolean(
        string='Keep re-editing Product active',
        help='This will allow you to define if those Product passed back to '
        'draft are still activated or not')

    def _get_parameter(self, key, default=False):
        param_obj = self.env['ir.config_parameter']
        rec = param_obj.search([('key', '=', key)])
        return rec or default

    def _write_or_create_param(self, key, value):
        param_obj = self.env['ir.config_parameter']
        rec = self._get_parameter(key)
        if rec:
            if not value:
                rec.unlink()
            else:
                rec.value = value
        elif value:
            param_obj.create({'key': key, 'value': value})

    @api.multi
    def get_default_parameters(self):
        def get_value(key, default=''):
            rec = self._get_parameter(key)
            return rec and rec.value or default
        return {
            'active_product_draft': get_value('active.product.draft', False),
        }

    @api.multi
    def set_parameters(self):
        self._write_or_create_param(
            'active.product.draft', self.active_product_draft)
