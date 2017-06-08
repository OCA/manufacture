# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    machines = fields.Many2many('machinery', 'machine_user_rel', 'user_id',
                                'machine_id', 'Machines')
