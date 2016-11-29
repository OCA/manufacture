# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, _, api


class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'
    default_create_project = fields.Boolean(
        string=_("Create projects from manufacturing orders"),
        help=_("""Automatically create projects from manufacturing orders if a
                 project is not assigned."""),
        default_model="mrp.production",
                 )
    default_create_tasks = fields.Boolean(
        string=_("Create tasks for each work order in production"),
        help=_(""" Automatically create tasks linked to manufacturing orders in
               assigned project."""),
        default_model="mrp.production"
    )


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
    def get_default_create(self, fields):
        def get_value(key, default=True):
            rec = self._get_parameter(key)
            return rec and rec.value or default
        return {
            'default_create_project': get_value('default.create.project', True),
            'default_create_tasks': get_value('default.create.tasks', True),
        }

    @api.multi
    def set_parameter_cycle_bom(self):
        self._write_or_create_param('cycle.by.bom', self.cycle_by_bom)

