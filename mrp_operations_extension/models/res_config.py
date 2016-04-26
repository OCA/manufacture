# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    group_mrp_workers = fields.Boolean(
        string='Manage operators in work centers',
        implied_group='mrp_operations_extension.group_mrp_workers')
    cycle_by_bom = fields.Boolean(string="Calc Cycles by BoM Quantity")

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
    def get_default_parameter_cycle_bom(self):
        def get_value(key, default=''):
            rec = self._get_parameter(key)
            return rec and rec.value or default
        return {'cycle_by_bom': get_value('cycle.by.bom', False)}

    @api.multi
    def set_parameter_cycle_bom(self):
        self._write_or_create_param('cycle.by.bom', self.cycle_by_bom)
