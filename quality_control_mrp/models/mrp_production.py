# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

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
        string='Inspections', help="Inspections related to this production.")
    created_inspections = fields.Integer(
        compute="_count_inspections", string="Created inspections")
    done_inspections = fields.Integer(
        compute="_count_inspections", string="Done inspections")
    passed_inspections = fields.Integer(
        compute="_count_inspections", string="Inspections OK")
    failed_inspections = fields.Integer(
        compute="_count_inspections", string="Inspections failed")

    @api.v7
    def action_produce(self, cr, uid, production_id, production_qty,
                       production_mode, wiz=False, context=None):
        production = self.browse(cr, uid, production_id, context=context)
        production.action_produce(
            production_id, production_qty, production_mode, wiz=wiz)

    @api.v8
    def action_produce(self, production_id, production_qty, production_mode,
                       wiz=False):
        res = super(MrpProduction, self).action_produce(
            production_id, production_qty, production_mode, wiz=wiz)
        if production_mode == 'consume_produce':
            inspection_model = self.env['qc.inspection']
            for move in self.move_created_ids2:
                qc_trigger = self.env.ref('quality_control_mrp.qc_trigger_mrp')
                tests = set()
                for model in ['qc.trigger.product_category_line',
                              'qc.trigger.product_template_line',
                              'qc.trigger.product_line']:
                    tests = tests.union(self.env[model].get_test_for_product(
                        qc_trigger, move.product_id))
                for test in tests:
                    inspection_model._make_inspection(move, test)
        return res
