# -*- coding: utf-8 -*-
#  Copyright 2019 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class QcTestQuestion(models.Model):
    _inherit = 'qc.test.question'

    code = fields.Char(
        help="Used for the evaluation of formulas: "
             "name of the variable corresponding to this question's value.")
    formula = fields.Text(
        help="Python formula for evaluating the current question."
             "Provided values are 'input_value' and "
             "the values of all the previous questions "
             "(the variable name is the 'code' field).")
