# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class MachineModel(models.Model):
    _name = 'machine.model'
    _description = 'Machine model'

    name = fields.Char('Name')
    model_type = fields.Char('Type')
