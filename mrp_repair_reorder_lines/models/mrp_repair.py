# -*- coding: utf-8 -*-
# Copyright 2016 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class MrpRepairLine(models.Model):
    _inherit = 'mrp.repair.line'

    sequence = fields.Integer(
        string='Sequence', default=10,
        help="Gives the sequence of this line when displaying the repair.")
