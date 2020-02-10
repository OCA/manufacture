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

    def _get_pdf_line(self, bom_id, product_id=False, qty=1, child_bom_ids=[],
                      unfolded=False):
        res = super(ReportBomStructure, self)._get_pdf_line(
            bom_id, product_id, qty, child_bom_ids, unfolded)
        lines = self.env['mrp.bom.line'].search([('bom_id', '=', bom_id)])
        lines = {l.product_id.display_name: l for l in lines}
        for res_line in res['lines']:
            line = lines.get(res_line['name'])
            res_line['description'] = line and line.description
        return res
