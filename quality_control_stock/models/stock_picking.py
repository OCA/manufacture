# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    @api.depends('qc_inspections', 'qc_inspections.state')
    def _count_inspections(self):
        self.created_inspections = len(self.qc_inspections)
        self.passed_inspections = len([x for x in self.qc_inspections if
                                       x.state == 'success'])
        self.failed_inspections = len([x for x in self.qc_inspections if
                                       x.state == 'failed'])
        self.done_inspections = (self.passed_inspections +
                                 self.failed_inspections)

    qc_inspections = fields.One2many(
        comodel_name='qc.inspection', inverse_name='picking', copy=False,
        string='Inspections', help="Inspections related to this picking.")
    created_inspections = fields.Integer(
        compute="_count_inspections", string="Created inspections")
    done_inspections = fields.Integer(
        compute="_count_inspections", string="Done inspections")
    passed_inspections = fields.Integer(
        compute="_count_inspections", string="Inspections OK")
    failed_inspections = fields.Integer(
        compute="_count_inspections", string="Inspections failed")

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        inspection_model = self.env['qc.inspection']
        for operation in self.pack_operation_ids:
            qc_trigger = self.env['qc.trigger'].search(
                [('picking_type', '=', self.picking_type_id.id)])
            tests = set()
            for model in ['qc.trigger.product_category_line',
                          'qc.trigger.product_template_line',
                          'qc.trigger.product_line']:
                tests = tests.union(self.env[model].get_test_for_product(
                    qc_trigger, operation.product_id))
            for test in tests:
                inspection_model._make_inspection(operation, test)
        return res
