# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
from openerp.addons import decimal_precision as dp


class MrpRouting(models.Model):
    _inherit = 'mrp.routing'

    @api.one
    @api.constrains('workcenter_lines')
    def _check_produce_operation(self):
        num_produce = len(self.workcenter_lines.filtered('do_production'))
        if num_produce != 1 and self.workcenter_lines:
            raise Warning(_("There must be one and only one operation with "
                            "'Produce here' check marked."))


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    operation = fields.Many2one('mrp.routing.operation', string='Operation')
    op_wc_lines = fields.One2many(
        'mrp.operation.workcenter', 'routing_workcenter',
        string='Possible work centers for this operation')
    do_production = fields.Boolean(
        string='Produce here',
        help="If enabled, the production and movement to stock of the final "
             "products will be done in this operation. There can be only one "
             "operation per route with this check marked.")
    previous_operations_finished = fields.Boolean(
        string='Previous operations finished')
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                      domain=[('code', '=', 'outgoing')])

    @api.constrains('op_wc_lines')
    def _check_default_op_wc_lines(self):
        num_default = len(self.op_wc_lines.filtered('default'))
        if num_default != 1 and self.op_wc_lines:
            raise Warning(
                _('There must be one and only one line set as default.'))

    @api.one
    @api.onchange('operation')
    def onchange_operation(self):
        if self.operation:
            self.name = self.operation.name
            self.note = self.operation.description
            self.picking_type_id = self.operation.picking_type_id
            self.op_wc_lines = False
            op_wc_lst = []
            is_default = True
            for operation_wc in self.operation.workcenters:
                data = {
                    'default': is_default,
                    'workcenter': operation_wc.id,
                    'capacity_per_cycle': operation_wc.capacity_per_cycle,
                    'time_efficiency': operation_wc.time_efficiency,
                    'time_cycle': operation_wc.time_cycle,
                    'time_start': operation_wc.time_start,
                    'time_stop': operation_wc.time_stop,
                    'op_number': self.operation.op_number,
                }
                op_wc_lst.append(data)
                is_default = False
            self.op_wc_lines = op_wc_lst

    @api.one
    @api.onchange('op_wc_lines')
    def onchange_lines_default(self):
        line = self.op_wc_lines.filtered('default')[:1]
        self.workcenter_id = line.workcenter
        data_source = line if line.custom_data else line.workcenter
        self.cycle_nbr = data_source.capacity_per_cycle
        self.hour_nbr = data_source.time_cycle


class MrpOperationWorkcenter(models.Model):
    _name = 'mrp.operation.workcenter'
    _description = 'MRP Operation Workcenter'

    custom_data = fields.Boolean(
        string="Custom", default=False,
        help="If you mark this check, this means that the work center in this "
             "routing has different capacity data than the defined on the "
             "work center itself")
    workcenter = fields.Many2one(
        'mrp.workcenter', string='Workcenter', required=True)
    routing_workcenter = fields.Many2one(
        'mrp.routing.workcenter', 'Routing workcenter', required=True,
        ondelete="cascade")
    time_efficiency = fields.Float('Efficiency factor')
    capacity_per_cycle = fields.Float('Capacity per cycle')
    time_cycle = fields.Float(
        string='Time for 1 cycle (hours)', help="Duration for one cycle.")
    time_start = fields.Float(
        string='Time before prod.', help="Duration for the setup.")
    time_stop = fields.Float(
        string='Time after prod.', help="Duartion for the cleaning.")
    op_number = fields.Integer('# operators', default='0')
    op_avg_cost = fields.Float(
        string='Operator average hourly cost',
        digits=dp.get_precision('Product Price'))
    default = fields.Boolean('Default')

    @api.one
    @api.onchange('workcenter', 'custom_data')
    def onchange_workcenter(self):
        if self.workcenter:
            self.capacity_per_cycle = self.workcenter.capacity_per_cycle
            self.time_efficiency = self.workcenter.time_efficiency
            self.time_cycle = self.workcenter.time_cycle
            self.time_start = self.workcenter.time_start
            self.time_stop = self.workcenter.time_stop
            self.op_number = self.workcenter.op_number
            self.op_avg_cost = self.workcenter.op_avg_cost
