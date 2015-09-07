# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    group_mrp_workers = fields.Boolean(
        string='Manage operators in work centers ',
        implied_group='mrp_operations_extension.group_mrp_workers')
