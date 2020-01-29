# -*- coding: utf-8 -*-
#  Copyright 2019 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'
    _order = 'sequence, id'

    code = fields.Char(
        help="Used for the evaluation of formulas: "
             "name of the variable corresponding to "
             "this inspection line's value.")
    sequence = fields.Integer()
    formula = fields.Text(
        help="Python formula for evaluating the current inspection line."
             "Provided values are 'input_value' and "
             "the values of all the previous inspection lines "
             "(the variable name is the 'code' field).")
    input_value = fields.Char()

    @api.multi
    def calculate_value(self):
        for line in self.filtered('formula'):
            formula_res = safe_eval(
                line.formula, line._prepare_formula_dict())
            if line.question_type == 'qualitative':
                line.qualitative_value = formula_res
            elif line.question_type == 'quantitative':
                line.quantitative_value = formula_res

    @api.multi
    def _prepare_formula_dict(self):
        self.ensure_one()
        formula_dict = {'input_value': self.input_value}
        # Compute all the previous inspection lines
        previous_lines = self.inspection_id.inspection_lines.filtered(
            lambda l: l.sequence <= self.sequence) - self
        for line in previous_lines:
            line_value = 0
            if line.question_type == 'qualitative':
                line_value = line.qualitative_value
            elif line.question_type == 'quantitative':
                line_value = line.quantitative_value
            formula_dict.update({line.code: line_value})

        return formula_dict

    @api.multi
    def write(self, vals):
        res = super(QcInspectionLine, self).write(vals)
        # If any of the following fields is modified,
        # recompute all the inspection lines of its inspection
        # because the result might change / be invalid
        formula_fields = ['inspection_id',
                          'code', 'input_value', 'formula', 'sequence']
        if any(ff in vals for ff in formula_fields):
            self.mapped('inspection_id').calculate_lines_values()
        return res
