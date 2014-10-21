# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import models, fields, api, exceptions, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    @api.depends('analytic_line_ids', 'analytic_line_ids.estim_std_cost',
                 'product_qty')
    def get_unit_std_cost(self):
        self.std_cost = sum([line.estim_std_cost for line in
                             self.analytic_line_ids])
        self.unit_std_cost = self.std_cost / self.product_qty

    @api.one
    @api.depends('analytic_line_ids', 'analytic_line_ids.estim_avg_cost',
                 'product_qty')
    def get_unit_avg_cost(self):
        self.avg_cost = sum([line.estim_avg_cost for line in
                             self.analytic_line_ids])
        self.unit_avg_cost = self.avg_cost / self.product_qty

    @api.one
    def _count_created_estimated_cost(self):
        analytic_line_obj = self.env['account.analytic.line']
        cond = [('mrp_production_id', '=', self.id),
                ('task_id', '=', False)]
        analytic_lines = analytic_line_obj.search(cond)
        self.created_estimated_cost = len(analytic_lines)

    active = fields.Boolean(
        'Active', default=lambda self: self.env.context.get('default_active',
                                                            True))
    name = fields.Char(
        string='Referencen', required=True, readonly=True, copy="False",
        states={'draft': [('readonly', False)]}, default="/")
    created_estimated_cost = fields.Integer(
        compute="_count_created_estimated_cost", string="Estimated Costs")
    std_cost = fields.Float(string="Estimated Standard Cost",
                            compute="get_unit_std_cost", store=True)
    avg_cost = fields.Float(string="Estimated Average Cost",
                            compute="get_unit_avg_cost", store=True)
    unit_std_cost = fields.Float(string="Estimated Standard Unit Cost",
                                 compute="get_unit_std_cost", store=True)
    unit_avg_cost = fields.Float(string="Estimated Average Unit Cost",
                                 compute="get_unit_avg_cost", store=True)
    product_manual_cost = fields.Float(
        string="Product Manual Cost",
        related="product_id.manual_standard_cost")
    product_cost = fields.Float(string="Product Cost",
                                related="product_id.standard_price")
    analytic_line_ids = fields.One2many("account.analytic.line",
                                        "mrp_production_id",
                                        string="Cost Lines")

    @api.model
    def create(self, values):
        sequence_obj = self.pool['ir.sequence']
        if 'active' not in values or values['active']:
            values['active'] = True
            values['name'] = sequence_obj.get(self._cr, self._uid,
                                              'mrp.production')
        else:
            values['name'] = sequence_obj.get(self._cr, self._uid,
                                              'fictitious.mrp.production')
        return super(MrpProduction, self).create(values)

    @api.multi
    def unlink(self):
        analytic_line_obj = self.env['account.analytic.line']
        for production in self:
            cond = [('mrp_production_id', '=', production.id)]
            analytic_line_obj.search(cond).unlink()
            if production.project_id.automatic_creation:
                production.project_id.unlink()
                analytic_lines = analytic_line_obj.search(
                    [('account_id', '=', production.analytic_account_id.id)])
                if not analytic_lines:
                    production.analytic_account_id.unlink()
        return super(MrpProduction, self).unlink()

    @api.multi
    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        self.calculate_production_estimated_cost()
        return res

    @api.multi
    def action_compute(self, properties=None):
        project_obj = self.env['project.project']
        res = super(MrpProduction, self).action_compute(properties=properties)
        for record in self:
            if not record.project_id:
                project = project_obj.search([('name', '=', record.name)],
                                             limit=1)
                if not project:
                    project_vals = {'name': record.name,
                                    'use_tasks': True,
                                    'use_timesheets': True,
                                    'use_issues': True,
                                    'automatic_creation': True,
                                    }
                    project = project_obj.create(project_vals)
                record.project_id = project.id
                record.analytic_account_id = project.analytic_account_id.id
        return res

    @api.multi
    def action_show_estimated_costs(self):
        self.ensure_one()
        analytic_line_obj = self.env['account.analytic.line']
        id2 = self.env.ref(
            'mrp_production_project_estimated_cost.estimated_cost_list_view')
        search_view = self.env.ref('mrp_project_link.account_analytic_line'
                                   '_mrp_search_view')
        analytic_line_list = analytic_line_obj.search(
            [('mrp_production_id', '=', self.id),
             ('task_id', '=', False)])
        self = self.with_context(search_default_group_production=1,
                                 search_default_group_workorder=1,
                                 search_default_group_journal=1)
        return {
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.analytic.line',
            'views': [(id2.id, 'tree')],
            'search_view_id': search_view.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': "[('id','in',[" +
            ','.join(map(str, analytic_line_list.ids)) + "])]",
            'context': self.env.context
            }

    @api.multi
    def calculate_production_estimated_cost(self):
        analytic_line_obj = self.env['account.analytic.line']
        for record in self:
            cond = [('mrp_production_id', '=', record.id)]
            analytic_line_obj.search(cond).unlink()
            journal = record.env.ref('mrp_production_project_estimated_cost.'
                                     'analytic_journal_materials', False)
            for line in record.product_lines:
                if not line.product_id:
                    raise exceptions.Warning(
                        _("One consume line has no product assigned."))
                name = _('%s-%s' % (record.name, line.work_order.name or ''))
                vals = record._prepare_estim_cost_analytic_line(
                    journal, name, record, line.work_order, line.product_id,
                    line.product_qty)
                analytic_line_obj.create(vals)
            journal = record.env.ref('mrp_production_project_estimated_cost.'
                                     'analytic_journal_machines', False)
            for line in record.workcenter_lines:
                op_wc_lines = line.routing_wc_line.op_wc_lines
                wc = op_wc_lines.filtered(lambda r: r.workcenter ==
                                          line.workcenter_id) or \
                    line.workcenter_id
                if (wc.time_start and line.workcenter_id.pre_op_product):
                    name = (_('%s-%s Pre-operation') %
                            (record.name, line.workcenter_id.name))
                    vals = record._prepare_estim_cost_analytic_line(
                        journal, name, record, line,
                        line.workcenter_id.pre_op_product, wc.time_start)
                    amount = line.workcenter_id.pre_op_product.standard_price
                    vals['amount'] = amount
                    analytic_line_obj.create(vals)
                if (wc.time_stop and line.workcenter_id.post_op_product):
                    name = (_('%s-%s Post-operation') %
                            (record.name, line.workcenter_id.name))
                    vals = record._prepare_estim_cost_analytic_line(
                        journal, name, record, line,
                        line.workcenter_id.post_op_product, wc.time_stop)
                    amount = line.workcenter_id.post_op_product.standard_price
                    vals['amount'] = amount
                    analytic_line_obj.create(vals)
                if line.cycle and line.workcenter_id.costs_cycle:
                    if not line.workcenter_id.product_id:
                        raise exceptions.Warning(
                            _("There is at least this workcenter without "
                              "product: %s") % line.workcenter_id.name)
                    name = (_('%s-%s-C-%s') %
                            (record.name, line.routing_wc_line.operation.code,
                             line.workcenter_id.name))
                    vals = record._prepare_estim_cost_analytic_line(
                        journal, name, record, line,
                        line.workcenter_id.product_id, line.cycle)
                    cost = line.workcenter_id.costs_cycle
                    vals['estim_avg_cost'] = line.cycle * cost
                    vals['estim_std_cost'] = vals['estim_avg_cost']
                    analytic_line_obj.create(vals)
                if line.hour and line.workcenter_id.costs_hour:
                    if not line.workcenter_id.product_id:
                        raise exceptions.Warning(
                            _("There is at least this workcenter without "
                              "product: %s") % line.workcenter_id.name)
                    name = (_('%s-%s-H-%s') %
                            (record.name, line.routing_wc_line.operation.code,
                             line.workcenter_id.name))
                    hour = line.hour
                    if wc.time_stop and not line.workcenter_id.post_op_product:
                        hour += wc.time_stop
                    if wc.time_start and not line.workcenter_id.pre_op_product:
                        hour += wc.time_start
                    vals = record._prepare_estim_cost_analytic_line(
                        journal, name, record, line,
                        line.workcenter_id.product_id, hour)
                    cost = line.workcenter_id.costs_hour
                    vals['estim_avg_cost'] = hour * cost
                    vals['estim_std_cost'] = vals['estim_avg_cost']
                    analytic_line_obj.create(vals)
                if wc.op_number > 0 and line.hour:
                    if not line.workcenter_id.product_id:
                        raise exceptions.Warning(
                            _("There is at least this workcenter without "
                              "product: %s") % line.workcenter_id.name)
                    journal_wk = record.env.ref(
                        'mrp_production_project_estimated_cost.analytic_'
                        'journal_operators', False)
                    name = (_('%s-%s-%s') %
                            (record.name, line.routing_wc_line.operation.code,
                             line.workcenter_id.product_id.name))
                    vals = record._prepare_estim_cost_analytic_line(
                        journal_wk, name, record, line,
                        line.workcenter_id.product_id,
                        line.hour * wc.op_number)
                    vals['estim_avg_cost'] = (wc.op_number * wc.op_avg_cost *
                                              line.hour)
                    vals['estim_std_cost'] = vals['estim_avg_cost']
                    analytic_line_obj.create(vals)

    def _prepare_estim_cost_analytic_line(self, journal, name, production,
                                          workorder, product, qty):
        analytic_line_obj = self.env['account.analytic.line']
        general_account = (product.property_account_income or
                           product.categ_id.property_account_income_categ or
                           False)
        if not general_account:
            raise exceptions.Warning(
                _('You must define Income account in the product "%s", or in'
                  ' the product category') % (product.name))
        if not self.analytic_account_id:
            raise exceptions.Warning(
                _('You must define one Analytic Account for this MO: %s') %
                (production.name))
        vals = {
            'name': name,
            'mrp_production_id': production.id,
            'workorder': workorder.id,
            'account_id': self.analytic_account_id.id,
            'journal_id': journal.id,
            'user_id': self._uid,
            'date': analytic_line_obj._get_default_date(),
            'product_id': product.id,
            'unit_amount': qty,
            'product_uom_id': product.uom_id.id,
            'general_account_id': general_account.id,
            'estim_std_cost': qty * product.manual_standard_cost,
            'estim_avg_cost': qty * product.standard_price,
        }
        return vals

    @api.multi
    def load_product_std_price(self):
        for record in self:
            product = record.product_id
            if record.unit_std_cost:
                product.manual_standard_cost = record.unit_std_cost
