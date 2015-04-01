# -*- coding: utf-8 -*-
# (c) 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from openerp.addons.quality_control.models.qc_trigger_line import\
    _filter_trigger_lines


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
            trigger_lines = set()
            for model in ['qc.trigger.product_category_line',
                          'qc.trigger.product_template_line',
                          'qc.trigger.product_line']:
                partner = (self.partner_id
                           if qc_trigger.partner_selectable else False)
                trigger_lines = trigger_lines.union(
                    self.env[model].get_trigger_line_for_product(
                        qc_trigger, operation.product_id, partner=partner))
            for trigger_line in _filter_trigger_lines(trigger_lines):
                inspection_model._make_inspection(operation, trigger_line)
        return res
