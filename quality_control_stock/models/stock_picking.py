# -*- coding: utf-8 -*-
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.quality_control.models.qc_trigger_line import\
    _filter_trigger_lines


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    @api.depends('qc_inspections', 'qc_inspections.state')
    def _compute_count_inspections(self):
        for picking in self:
            picking.created_inspections = len(picking.qc_inspections)
            picking.passed_inspections = \
                len([x for x in picking.qc_inspections
                     if x.state == 'success'])
            picking.failed_inspections = \
                len([x for x in picking.qc_inspections
                     if x.state == 'failed'])
            picking.done_inspections = \
                (picking.passed_inspections + picking.failed_inspections)

    qc_inspections = fields.One2many(
        comodel_name='qc.inspection', inverse_name='picking', copy=False,
        string='Inspections', help="Inspections related to this picking.")
    created_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Created inspections")
    done_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Done inspections")
    passed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections OK")
    failed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections failed")

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
