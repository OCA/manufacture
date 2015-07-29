# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    init_without_material = fields.Boolean(
        string='Init without material',
        help="If enabled, current operation could be initialized even if there"
        "is no material assigned to it.")
