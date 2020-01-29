# -*- coding: utf-8 -*-
#  Copyright 2019 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.multi
    def _prepare_inspection_line(self, test, line, fill=None):
        line_data = super(QcInspection, self) \
            ._prepare_inspection_line(test, line, fill=fill)
        line_data.update({
            'code': line.code,
            'sequence': line.sequence,
            'formula': line.formula
        })
        return line_data

    @api.multi
    def calculate_lines_values(self):
        self.mapped('inspection_lines').calculate_value()
