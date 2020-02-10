# Copyright 2020 PlanetaTIC <info@planetatic.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        res = super(ReportBomStructure, self)._get_bom_lines(
            bom, bom_quantity, product, line_id, level)
        lines = self.env['mrp.bom.line'].search([('bom_id', '=', bom.id)])
        lines = {l.id: l for l in lines}
        for res_line in res[0]:
            line = lines.get(res_line['line_id'])
            res_line['description'] = line and line.description
        return res

    def _get_line_vals(self, bom_line):
        res = super(ReportBomStructure, self)._get_line_vals(bom_line)
        res['description'] = bom_line.get('description')
        return res
