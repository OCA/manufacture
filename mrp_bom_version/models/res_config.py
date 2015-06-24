# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    group_mrp_bom_version = fields.Boolean(
        string='Allow to re-edit BoMs',
        implied_group='mrp_bom_version.group_mrp_bom_version',
        help='The active state may be passed back to state draft')
