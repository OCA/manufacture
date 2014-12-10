# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api, exceptions, _


class QcSample(models.Model):
    _name = 'qc.sample'
    _description = 'Quality control inspection samples definition'

    name = fields.Char(string='Description', required=True, select=True)
    sample_lines = fields.One2many(
        comodel_name='qc.sample.line', inverse_name='sample',
        string='Sample lines')

    @api.one
    @api.constrains('sample_lines')
    def _check_ranges(self):
        pass

    @api.multi
    def get_samples_number(self, qty):
        self.ensure_one()
        for line in self.sample_lines:
            if line.min_qty <= qty <= line.max_qty:
                return line.samples_taken
        return 0


class QcSample(models.Model):
    _name = 'qc.sample.line'
    _description = 'Quality control inspection sample line'

    sample = fields.Many2one(
        comodel_name='qc.sample', string='Sample', ondelete='cascade')
    min_qty = fields.Integer('From', required=True)
    max_qty = fields.Integer('To', required=True)
    samples_taken = fields.Integer('Samples taken', required=True)

    @api.one
    @api.constrains('min_qty', 'max_qty')
    def _check_interval(self):
        if self.min_qty > self.max_qty:
            raise exceptions.Warning(
                _('Min value cannot be bigger than max value.'))