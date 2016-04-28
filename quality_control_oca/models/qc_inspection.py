# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class QcInspection(models.Model):
    _name = 'qc.inspection'
    _description = 'Quality control inspection'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.one
    @api.depends('inspection_lines', 'inspection_lines.success')
    def _success(self):
        self.success = all([x.success for x in self.inspection_lines])

    @api.multi
    def _links_get(self):
        link_obj = self.env['res.request.link']
        return [(r.object, r.name) for r in link_obj.search([])]

    @api.one
    @api.depends('object_id')
    def _get_product(self):
        if self.object_id and self.object_id._name == 'product.product':
            self.product = self.object_id
        else:
            self.product = False

    name = fields.Char(
        string='Inspection number', required=True, default='/', select=True,
        readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    date = fields.Datetime(
        string='Date', required=True, readonly=True, copy=False,
        default=fields.Datetime.now,
        states={'draft': [('readonly', False)]}, select=True)
    object_id = fields.Reference(
        string='Reference', selection=_links_get, readonly=True,
        states={'draft': [('readonly', False)]}, ondelete="set null")
    product = fields.Many2one(
        comodel_name="product.product", compute="_get_product", store=True,
        help="Product associated with the inspection")
    qty = fields.Float(string="Quantity", default=1.0)
    test = fields.Many2one(
        comodel_name='qc.test', string='Test', readonly=True, select=True)
    inspection_lines = fields.One2many(
        comodel_name='qc.inspection.line', inverse_name='inspection_id',
        string='Inspection lines', readonly=True,
        states={'ready': [('readonly', False)]})
    internal_notes = fields.Text(string='Internal notes')
    external_notes = fields.Text(
        string='External notes',
        states={'success': [('readonly', True)],
                'failed': [('readonly', True)]})
    state = fields.Selection(
        [('draft', 'Draft'),
         ('ready', 'Ready'),
         ('waiting', 'Waiting supervisor approval'),
         ('success', 'Quality success'),
         ('failed', 'Quality failed'),
         ('canceled', 'Canceled')],
        string='State', readonly=True, default='draft')
    success = fields.Boolean(
        compute="_success", string='Success',
        help='This field will be marked if all tests have succeeded.',
        store=True)
    auto_generated = fields.Boolean(
        string='Auto-generated', readonly=True, copy=False,
        help='If an inspection is auto-generated, it can be canceled nor '
             'removed.')
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'qc.inspection'))
    user = fields.Many2one(
        comodel_name='res.users', string='Responsible',
        track_visibility='always', default=lambda self: self.env.user)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('qc.inspection')
        return super(QcInspection, self).create(vals)

    @api.multi
    def unlink(self):
        for inspection in self:
            if inspection.auto_generated:
                raise exceptions.Warning(
                    _("You cannot remove an auto-generated inspection."))
            if inspection.state != 'draft':
                raise exceptions.Warning(
                    _("You cannot remove an inspection that is not in draft "
                      "state."))
        return super(QcInspection, self).unlink()

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_todo(self):
        for inspection in self:
            if not inspection.test:
                raise exceptions.Warning(
                    _("You must first set the test to perform."))
        self.write({'state': 'ready'})

    @api.multi
    def action_confirm(self):
        for inspection in self:
            for line in inspection.inspection_lines:
                if line.question_type == 'qualitative':
                    if not line.qualitative_value:
                        raise exceptions.Warning(
                            _("You should provide an answer for all "
                              "qualitative questions."))
                else:
                    if not line.uom_id:
                        raise exceptions.Warning(
                            _("You should provide a unit of measure for "
                              "quantitative questions."))
            if inspection.success:
                inspection.state = 'success'
            else:
                inspection.state = 'waiting'

    @api.multi
    def action_approve(self):
        for inspection in self:
            if inspection.success:
                inspection.state = 'success'
            else:
                inspection.state = 'failed'

    @api.multi
    def action_cancel(self):
        self.write({'state': 'canceled'})

    @api.multi
    def set_test(self, trigger_line, force_fill=False):
        for inspection in self:
            header = self._prepare_inspection_header(
                inspection.object_id, trigger_line)
            del header['state']  # don't change current status
            del header['auto_generated']  # don't change auto_generated flag
            del header['user']  # don't change current user
            inspection.write(header)
            inspection.inspection_lines.unlink()
            inspection.inspection_lines = inspection._prepare_inspection_lines(
                trigger_line.test, force_fill=force_fill)

    @api.multi
    def _make_inspection(self, object_ref, trigger_line):
        """Overridable hook method for creating inspection from test.
        :param object_ref: Object instance
        :param trigger_line: Trigger line instance
        :return: Inspection object
        """
        inspection = self.create(self._prepare_inspection_header(
            object_ref, trigger_line))
        inspection.set_test(trigger_line)
        return inspection

    @api.multi
    def _prepare_inspection_header(self, object_ref, trigger_line):
        """Overridable hook method for preparing inspection header.
        :param object_ref: Object instance
        :param trigger_line: Trigger line instance
        :return: List of values for creating the inspection
        """
        return {
            'object_id': object_ref and '%s,%s' % (object_ref._name,
                                                   object_ref.id) or False,
            'state': 'ready',
            'test': trigger_line.test.id,
            'user': trigger_line.user.id,
            'auto_generated': True,
        }

    @api.multi
    def _prepare_inspection_lines(self, test, force_fill=False):
        new_data = []
        for line in test.test_lines:
            data = self._prepare_inspection_line(
                test, line, fill=test.fill_correct_values or force_fill)
            new_data.append((0, 0, data))
        return new_data

    @api.multi
    def _prepare_inspection_line(self, test, line, fill=None):
        data = {
            'name': line.name,
            'test_line': line.id,
            'notes': line.notes,
            'min_value': line.min_value,
            'max_value': line.max_value,
            'test_uom_id': line.uom_id.id,
            'uom_id': line.uom_id.id,
            'question_type': line.type,
            'possible_ql_values': [x.id for x in line.ql_values]
        }
        if fill:
            if line.type == 'qualitative':
                # Fill with the first correct value found
                for value in line.ql_values:
                    if value.ok:
                        data['qualitative_value'] = value.id
                        break
            else:
                # Fill with a value inside the interval
                data['quantitative_value'] = (line.min_value +
                                              line.max_value) * 0.5
        return data


class QcInspectionLine(models.Model):
    _name = 'qc.inspection.line'
    _description = "Quality control inspection line"

    @api.one
    @api.depends('question_type', 'uom_id', 'test_uom_id', 'max_value',
                 'min_value', 'quantitative_value', 'qualitative_value',
                 'possible_ql_values')
    def quality_test_check(self):
        if self.question_type == 'qualitative':
            self.success = self.qualitative_value.ok
        else:
            if self.uom_id.id == self.test_uom_id.id:
                amount = self.quantitative_value
            else:
                amount = self.env['product.uom']._compute_qty(
                    self.uom_id.id, self.quantitative_value,
                    self.test_uom_id.id)
            self.success = self.max_value >= amount >= self.min_value

    @api.one
    @api.depends('possible_ql_values', 'min_value', 'max_value', 'test_uom_id',
                 'question_type')
    def get_valid_values(self):
        if self.question_type == 'qualitative':
            self.valid_values = ", ".join([x.name for x in
                                           self.possible_ql_values if x.ok])
        else:
            self.valid_values = "%s-%s" % (self.min_value, self.max_value)
            if self.env.ref("product.group_uom") in self.env.user.groups_id:
                self.valid_values += " %s" % self.test_uom_id.name

    inspection_id = fields.Many2one(
        comodel_name='qc.inspection', string='Inspection', ondelete='cascade')
    name = fields.Char(string="Question", readonly=True)
    product = fields.Many2one(
        comodel_name="product.product", related="inspection_id.product",
        store=True)
    test_line = fields.Many2one(
        comodel_name='qc.test.question', string='Test question',
        readonly=True)
    possible_ql_values = fields.Many2many(
        comodel_name='qc.test.question.value', string='Answers')
    quantitative_value = fields.Float(
        'Quantitative value', digits=(16, 5),
        help="Value of the result for a quantitative question.")
    qualitative_value = fields.Many2one(
        comodel_name='qc.test.question.value', string='Qualitative value',
        help="Value of the result for a qualitative question.",
        domain="[('id', 'in', possible_ql_values[0][2])]")
    notes = fields.Text(string='Notes')
    min_value = fields.Float(
        string='Min', digits=(16, 5), readonly=True,
        help="Minimum valid value for a quantitative question.")
    max_value = fields.Float(
        string='Max', digits=(16, 5), readonly=True,
        help="Maximum valid value for a quantitative question.")
    test_uom_id = fields.Many2one(
        comodel_name='product.uom', string='Test UoM', readonly=True,
        help="UoM for minimum and maximum values for a quantitative "
             "question.")
    test_uom_category = fields.Many2one(
        comodel_name="product.uom.categ", related="test_uom_id.category_id",
        store=True)
    uom_id = fields.Many2one(
        comodel_name='product.uom', string='UoM',
        domain="[('category_id', '=', test_uom_category)]",
        help="UoM of the inspection value for a quantitative question.")
    question_type = fields.Selection(
        [('qualitative', 'Qualitative'),
         ('quantitative', 'Quantitative')],
        string='Question type', readonly=True)
    valid_values = fields.Char(string="Valid values", store=True,
                               compute="get_valid_values")
    success = fields.Boolean(
        compute="quality_test_check", string="Success?", store=True)
