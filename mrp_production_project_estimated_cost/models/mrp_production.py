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
        self.std_cost = -(sum([line.estim_std_cost for line in
                               self.analytic_line_ids]))
        self.unit_std_cost = self.std_cost / self.product_qty

    @api.one
    @api.depends('analytic_line_ids', 'analytic_line_ids.estim_avg_cost',
                 'product_qty')
    def get_unit_avg_cost(self):
        self.avg_cost = -(sum([line.estim_avg_cost for line in
                               self.analytic_line_ids]))
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
    name = fields.Char(default="/")
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
    product_cost = fields.Float(
        string="Product Cost", related="product_id.cost_price")
    analytic_line_ids = fields.One2many(
        comodel_name="account.analytic.line", inverse_name="mrp_production_id",
        string="Cost Lines")

    @api.model
    def create(self, values):
        sequence_obj = self.env['ir.sequence']
        if values.get('active', True):
            values['active'] = True
            if values.get('name', '/') == '/':
                values['name'] = sequence_obj.get('mrp.production')
        else:
            values['name'] = sequence_obj.get('fictitious.mrp.production')
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
                    project_vals = {
                        'name': record.name,
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

    @api.model
    def _prepare_estimated_cost_analytic_line(
            self, journal, name, production, product, general_account=None,
            workorder=None, qty=1, std_cost=0, avg_cost=0):
        """
        Prepare the vals for creating an analytic entry for stimated cost
        :param journal: Journal of the entry
        :param name: Name of the entry
        :param production: Origin product
        :param product: Product for the entry
        :param general_account: General account for the entry
        :param workorder: Origin workorder
        :param qty: Quantity for the entry. This quantity will multiply both
        standard and average costs for the entry costs.
        :param std_cost: Cost for calculating estimated standard cost. If 0,
        then product manual standard cost will be used.
        :param avg_cost: Cost for calculating estimated average cost. If 0,
        then product cost will be used.
        :return: Dictionary with the analytic entry vals.
        """
        analytic_line_obj = self.env['account.analytic.line']
        property_obj = self.env['ir.property']
        if not general_account:
            general_account = (
                product.property_account_income or
                product.categ_id.property_account_income_categ or
                property_obj.get('property_account_expense_categ',
                                 'product.category'))
        if not production.analytic_account_id:
            raise exceptions.Warning(
                _('You must define one Analytic Account for this MO: %s') %
                (production.name))
        return {
            'name': name,
            'mrp_production_id': production.id,
            'workorder': workorder and workorder.id or False,
            'account_id': self.analytic_account_id.id,
            'journal_id': journal.id,
            'user_id': self.env.uid,
            'date': analytic_line_obj._get_default_date(),
            'product_id': product and product.id or False,
            'unit_amount': qty,
            'amount': 0,
            'product_uom_id': product.uom_id.id,
            'general_account_id': general_account.id,
            'estim_std_cost': -qty * (std_cost or
                                      product.manual_standard_cost),
            'estim_avg_cost': -qty * (avg_cost or product.cost_price),
        }

    @api.model
    def _create_material_estimated_cost(self, prod, product_line):
        if not product_line.product_id:
            raise exceptions.Warning(
                _("One consume line has no product assigned."))
        journal = self.env.ref('mrp.analytic_journal_materials', False)
        name = _('%s-%s' % (prod.name, product_line.work_order.name or ''))
        product = product_line.product_id
        qty = product_line.product_qty
        vals = self._prepare_estimated_cost_analytic_line(
            journal, name, prod, product, workorder=product_line.work_order,
            qty=qty)
        return self.env['account.analytic.line'].create(vals)

    @api.model
    def _create_pre_operation_estimated_cost(self, prod, wc, workorder):
        if (wc.time_start and workorder.workcenter_id.pre_op_product):
            product = workorder.workcenter_id.pre_op_product
            if not product:
                raise exceptions.Warning(
                    _("Workcenter '%s' doesn't have pre-operation costing "
                      "product.") % workorder.workcenter_id.name)
            journal = self.env.ref('mrp.analytic_journal_machines', False)
            name = (_('%s-%s Pre-operation') %
                    (prod.name, workorder.workcenter_id.name))
            vals = self._prepare_estimated_cost_analytic_line(
                journal, name, prod, product, workorder=workorder,
                qty=wc.time_start)
            return self.env['account.analytic.line'].create(vals)

    @api.model
    def _create_post_operation_estimated_cost(self, prod, wc, workorder):
        if (wc.time_stop and workorder.workcenter_id.post_op_product):
            product = workorder.workcenter_id.post_op_product
            if not product:
                raise exceptions.Warning(
                    _("Workcenter '%s' doesn't have post-operation costing "
                      "product.") % workorder.workcenter_id.name)
            journal = self.env.ref('mrp.analytic_journal_machines', False)
            name = (_('%s-%s Post-operation') %
                    (prod.name, workorder.workcenter_id.name))
            vals = self._prepare_estimated_cost_analytic_line(
                journal, name, prod, product, workorder=workorder,
                qty=wc.time_stop)
            return self.env['account.analytic.line'].create(vals)

    @api.model
    def _create_worcenter_cycles_estimated_cost(self, prod, wc, workorder):
        if workorder.cycle and workorder.workcenter_id.costs_cycle:
            journal = prod.env.ref('mrp.analytic_journal_machines', False)
            product = workorder.workcenter_id.product_id
            if not product:
                raise exceptions.Warning(
                    _("There is at least this workcenter without "
                      "product: %s") % workorder.workcenter_id.name)
            name = (_('%s-%s-C-%s') %
                    (prod.name, workorder.routing_wc_line.operation.code,
                     workorder.workcenter_id.name))
            cost = workorder.workcenter_id.costs_cycle
            vals = self._prepare_estimated_cost_analytic_line(
                journal, name, prod, product, workorder=workorder,
                qty=workorder.cycle, std_cost=cost, avg_cost=cost)
            return self.env['account.analytic.line'].create(vals)

    @api.model
    def _create_worcenter_hours_estimated_cost(self, prod, wc, workorder):
        if workorder.hour and workorder.workcenter_id.costs_hour:
            product = workorder.workcenter_id.product_id
            if not product:
                raise exceptions.Warning(
                    _("There is at least this workcenter without "
                      "product: %s") % workorder.workcenter_id.name)
            journal = self.env.ref('mrp.analytic_journal_machines', False)
            name = (_('%s-%s-H-%s') %
                    (prod.name, workorder.routing_wc_line.operation.code,
                     workorder.workcenter_id.name))
            cost = workorder.workcenter_id.costs_hour
            vals = self._prepare_estimated_cost_analytic_line(
                journal, name, prod, product, workorder=workorder,
                qty=workorder.hour, std_cost=cost, avg_cost=cost)
            return self.env['account.analytic.line'].create(vals)

    @api.model
    def _create_operators_estimated_cost(self, prod, wc, workorder):
        if wc.op_number > 0 and workorder.hour:
            product = workorder.workcenter_id.product_id
            if not product:
                raise exceptions.Warning(
                    _("There is at least this workcenter without "
                      "product: %s") % workorder.workcenter_id.name)
            journal = self.env.ref('mrp.analytic_journal_operators', False)
            name = (_('%s-%s-%s') %
                    (prod.name, workorder.routing_wc_line.operation.code,
                     product.name))
            cost = wc.op_avg_cost
            qty = workorder.hour * wc.op_number
            vals = self._prepare_estimated_cost_analytic_line(
                journal, name, prod, product, workorder=workorder, qty=qty,
                std_cost=cost, avg_cost=cost)
            return self.env['account.analytic.line'].create(vals)

    @api.multi
    def calculate_production_estimated_cost(self):
        analytic_line_obj = self.env['account.analytic.line']
        for record in self:
            cond = [('mrp_production_id', '=', record.id)]
            analytic_line_obj.search(cond).unlink()
            for product_line in record.product_lines:
                self._create_material_estimated_cost(
                    record, product_line)
            for line in record.workcenter_lines:
                op_wc_lines = line.routing_wc_line.op_wc_lines
                wc = op_wc_lines.filtered(lambda r: r.workcenter ==
                                          line.workcenter_id) or \
                    line.workcenter_id
                self._create_pre_operation_estimated_cost(record, wc, line)
                self._create_post_operation_estimated_cost(record, wc, line)
                done = self._create_worcenter_cycles_estimated_cost(
                    record, wc, line)
                if not done:
                    self._create_worcenter_hours_estimated_cost(
                        record, wc, line)
                self._create_operators_estimated_cost(record, wc, line)

    @api.multi
    def load_product_std_price(self):
        for record in self:
            product = record.product_id
            if record.unit_std_cost:
                product.manual_standard_cost = record.unit_std_cost

    @api.multi
    def _get_min_qty_for_production(self, routing=False):
        return 1
