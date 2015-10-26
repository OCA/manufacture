# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class QcInspectionSetTest(models.TransientModel):
    """This wizard is used to preset the test for a given
    inspection. This will not only fill in the 'test' field, but will
    also fill in all lines of the inspection with the corresponding lines of
    the template.
    """
    _name = 'qc.inspection.set.test'

    test = fields.Many2one(comodel_name='qc.test', string='Test')

    @api.multi
    def action_create_test(self):
        inspection = self.env['qc.inspection'].browse(
            self.env.context['active_id'])
        inspection.test = self.test
        inspection.inspection_lines.unlink()
        inspection.inspection_lines = inspection._prepare_inspection_lines(
            self.test)
        return True
