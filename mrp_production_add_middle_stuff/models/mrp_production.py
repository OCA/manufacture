# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    addition = fields.Boolean('Added Post-startup')
