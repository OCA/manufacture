# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    notes = fields.Html()
