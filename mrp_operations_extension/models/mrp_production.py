# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
import math


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    workcenter_lines = fields.One2many(readonly=False)
    date_planned = fields.Datetime(states={'draft': [('readonly', False)],
                                           'confirmed': [('readonly', False)],
                                           'ready': [('readonly', False)]})

    def _get_minor_sequence_operation(self, operations):
        return min(operations, key=lambda x: x.sequence)

    @api.model
    def _moves_assigned(self):
        res = super(MrpProduction, self)._moves_assigned()
        if res:
            return True
        operation = self._get_minor_sequence_operation(self.workcenter_lines)
        assigned_moves, no_assigned_products = \
            self._get_operation_moves(operation, state='assigned')
        return no_assigned_products == []

    @api.multi
    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        if (self.routing_id and
                not any([x.do_production for x in self.workcenter_lines])):
            raise exceptions.Warning(
                _("At least one work order must have checked 'Produce here'"))
        return res

    @api.multi
    def _action_compute_lines(self, properties=None):
        res = super(MrpProduction, self)._action_compute_lines(
            properties=properties)
        self._get_workorder_in_product_lines(
            self.workcenter_lines, self.product_lines, properties=properties)
        return res

    def _get_workorder_in_product_lines(
            self, workcenter_lines, product_lines, properties=None):
        for workorder in workcenter_lines:
            wc = workorder.routing_wc_line
            cycle = wc.cycle_nbr and int(math.ceil(self.product_qty /
                                                   wc.cycle_nbr)) or 0
            workorder.cycle = cycle
            workorder.hour = wc.hour_nbr * cycle
        for p_line in product_lines:
            for bom_line in self.bom_id.bom_line_ids:
                if bom_line.product_id.id == p_line.product_id.id:
                    for wc_line in workcenter_lines:
                        if wc_line.routing_wc_line.id == bom_line.operation.id:
                            p_line.work_order = wc_line.id
                            break
                elif bom_line.type == 'phantom':
                    bom_obj = self.env['mrp.bom']
                    bom_id = bom_obj._bom_find(
                        product_id=bom_line.product_id.id,
                        properties=properties)
                    for bom_line2 in bom_obj.browse(bom_id).bom_line_ids:
                        if bom_line2.product_id.id == p_line.product_id.id:
                            for wc_line in workcenter_lines:
                                if (wc_line.routing_wc_line.id ==
                                        bom_line2.operation.id):
                                    p_line.work_order = wc_line.id
                                    break

    @api.model
    def _make_production_consume_line(self, line):
        move_id = super(MrpProduction,
                        self)._make_production_consume_line(line)
        if line.work_order and move_id:
            move = self.env['stock.move'].browse(move_id)
            move.work_order = line.work_order.id
        return move_id


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    work_order = fields.Many2one('mrp.production.workcenter.line',
                                 'Work Order')


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    @api.one
    def _ready_materials(self):
        self.is_material_ready = True
        if self.product_line:
            moves = self.env['stock.move'].search([('work_order', '=',
                                                    self.id)])
            self.is_material_ready = not any(
                x not in ('assigned', 'cancel', 'done') for x in
                moves.mapped('state'))

    product_line = fields.One2many('mrp.production.product.line',
                                   'work_order', string='Product Lines')
    routing_wc_line = fields.Many2one('mrp.routing.workcenter',
                                      string='Routing WC Line')
    do_production = fields.Boolean(string='Produce here')
    time_start = fields.Float(string="Time Start")
    time_stop = fields.Float(string="Time Stop")
    move_lines = fields.One2many('stock.move', 'work_order',
                                 string='Moves')
    is_material_ready = fields.Boolean('Materials Ready',
                                       compute="_ready_materials")

    @api.one
    def action_assign(self):
        self.move_lines.action_assign()

    @api.one
    def force_assign(self):
        self.move_lines.force_assign()

    @api.multi
    def _load_mo_date_planned(self, production, date_planned):
        if date_planned < production.date_planned:
            production.write({'date_planned': date_planned})
            return True
        return False

    @api.model
    def create(self, vals):
        production_obj = self.env['mrp.production']
        dp = vals.get('date_planned', False)
        production_id = vals.get('production_id', False)
        if dp and production_id:
            production = production_obj.browse(production_id)
            self._load_mo_date_planned(production, dp)
        return super(MrpProductionWorkcenterLine, self).create(vals)

    @api.multi
    def write(self, vals, update=False):
        if vals.get('date_planned', False):
            dp = vals.get('date_planned')
            update = self._load_mo_date_planned(self.production_id, dp)
        res = super(MrpProductionWorkcenterLine, self).write(vals,
                                                             update=update)
        return res

    def check_minor_sequence_operations(self):
        seq = self.sequence
        for operation in self.production_id.workcenter_lines:
            if operation.sequence < seq and operation.state != 'done':
                return False
        return True

    def check_operation_moves_state(self, states):
        for move_line in self.move_lines:
            if move_line.state not in states:
                return False
        return True

    def action_start_working(self):
        if self.routing_wc_line.previous_operations_finished and \
                not self.check_minor_sequence_operations():
            raise exceptions.Warning(_("Previous operations not finished"))
        if not self.check_operation_moves_state(['assigned', 'cancel',
                                                 'done']):
            raise exceptions.Warning(
                _("Missing materials to start the production"))
        if self.production_id.state in ('confirmed', 'ready'):
            self.production_id.state = 'in_production'
        return super(MrpProductionWorkcenterLine, self).action_start_working()
