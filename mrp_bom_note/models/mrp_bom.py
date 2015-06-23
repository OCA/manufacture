# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    notes = fields.Html()
