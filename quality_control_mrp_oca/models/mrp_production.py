# -*- coding: utf-8 -*-
# (c) 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from openerp.addons.quality_control.models.qc_trigger_line import\
    _filter_trigger_lines


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    @api.depends('qc_inspections')
    def _count_inspections(self):
        self.created_inspections = len(self.qc_inspections)

    qc_inspections = fields.One2many(
        comodel_name='qc.inspection', inverse_name='production', copy=False,
        string='Inspections', help="Inspections related to this production.")
    created_inspections = fields.Integer(
        compute="_count_inspections", string="Created inspections")

    @api.model
    def action_produce(self, production_id, production_qty, production_mode,
                       wiz=False):
        res = super(MrpProduction, self).action_produce(
            production_id, production_qty, production_mode, wiz=wiz)
        if production_mode == 'consume_produce':
            inspection_model = self.env['qc.inspection']
            production = self.browse(production_id)
            for move in production.move_created_ids2:
                qc_trigger = self.env.ref('quality_control_mrp.qc_trigger_mrp')
                trigger_lines = set()
                for model in ['qc.trigger.product_category_line',
                              'qc.trigger.product_template_line',
                              'qc.trigger.product_line']:
                    trigger_lines = trigger_lines.union(
                        self.env[model].get_trigger_line_for_product(
                            qc_trigger, move.product_id))
                for trigger_line in _filter_trigger_lines(trigger_lines):
                    inspection_model._make_inspection(move, trigger_line)
        return res
