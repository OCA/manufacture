# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.multi
    def _prepare_inspection_lines(self, test, force_fill=False):
        res = super(QcInspection, self)._prepare_inspection_lines(
            test, force_fill=force_fill)
        if test.sample:
            num_samples = test.sample.get_samples_number(self.qty)
            if num_samples:
                i = 1
                new_data = []
                while i <= num_samples:
                    for line_tuple in res:
                        line = line_tuple[2].copy()
                        line['sample_number'] = i
                        new_data.append((0, 0, line))
                    i += 1
                return new_data
        return res


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'
    _order = 'sample_number, id'

    sample_number = fields.Integer(
        string='# sample', readonly=True)
