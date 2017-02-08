# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class QcTest(models.Model):
    """
    A test is a group of questions along with the values that make them valid.
    """
    _name = 'qc.test'
    _description = 'Quality control test'

    @api.multi
    def _links_get(self):
        link_obj = self.env['res.request.link']
        return [(r.object, r.name) for r in link_obj.search([])]

    active = fields.Boolean('Active', default=True)
    name = fields.Char(
        string='Name', required=True, translate=True, select=True)
    test_lines = fields.One2many(
        comodel_name='qc.test.question', inverse_name='test',
        string='Questions', copy=True)
    object_id = fields.Reference(
        string='Reference object', selection=_links_get,)
    fill_correct_values = fields.Boolean(
        string='Pre-fill with correct values')
    type = fields.Selection(
        [('generic', 'Generic'),
         ('related', 'Related')],
        string='Type', select=True, required=True, default='generic')
    category = fields.Many2one(
        comodel_name='qc.test.category', string='Category')
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'qc.test'))


class QcTestQuestion(models.Model):
    """Each test line is a question with its valid value(s)."""
    _name = 'qc.test.question'
    _description = 'Quality control question'
    _order = 'sequence, id'

    @api.one
    @api.constrains('ql_values')
    def _check_valid_answers(self):
        if (self.type == 'qualitative' and self.ql_values and
                not self.ql_values.filtered('ok')):
            raise exceptions.Warning(
                _("There isn't no value marked as OK. You have to mark at "
                  "least one."))

    @api.one
    @api.constrains('min_value', 'max_value')
    def _check_valid_range(self):
        if self.type == 'quantitative' and self.min_value > self.max_value:
            raise exceptions.Warning(
                _("Minimum value can't be higher than maximum value."))

    sequence = fields.Integer(
        string='Sequence', required=True, default="10")
    test = fields.Many2one(comodel_name='qc.test', string='Test')
    name = fields.Char(
        string='Name', required=True, select=True, translate=True)
    type = fields.Selection(
        [('qualitative', 'Qualitative'),
         ('quantitative', 'Quantitative')], string='Type', required=True)
    ql_values = fields.One2many(
        comodel_name='qc.test.question.value', inverse_name="test_line",
        string='Qualitative values', copy=True)
    notes = fields.Text(string='Notes')
    min_value = fields.Float(string='Min',
                             digits=dp.get_precision('Quality Control'))
    max_value = fields.Float(string='Max',
                             digits=dp.get_precision('Quality Control'),)
    uom_id = fields.Many2one(comodel_name='product.uom', string='Uom')


class QcTestQuestionValue(models.Model):
    _name = 'qc.test.question.value'
    _description = 'Possible values for qualitative questions.'

    test_line = fields.Many2one(
        comodel_name="qc.test.question", string="Test question")
    name = fields.Char(
        string='Name', required=True, select=True, translate=True)
    ok = fields.Boolean(
        string='Correct answer?',
        help="When this field is marked, the answer is considered correct.")
