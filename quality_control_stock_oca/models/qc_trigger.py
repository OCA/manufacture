# -*- coding: utf-8 -*-
# (c) 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class QcTrigger(models.Model):
    _inherit = 'qc.trigger'

    picking_type = fields.Many2one(
        comodel_name="stock.picking.type", readonly=True, ondelete="cascade")
