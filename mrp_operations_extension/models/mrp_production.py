# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    workcenter_lines = fields.One2many(readonly=False)
    date_planned = fields.Datetime(
        states={'draft': [('readonly', False)],
                'confirmed': [('readonly', False)],
                'ready': [('readonly', False)]})

    @api.multi
    def action_confirm(self):
        for prod in self:
            if (prod.workcenter_lines and
                    not len(prod.workcenter_lines.filtered('do_production'))):
                raise exceptions.Warning(
                    _("At least one work order must have checked 'Produce "
                      "here'"))
        return super(MrpProduction, self).action_confirm()

    @api.multi
    def _action_compute_lines(self, properties=None):
        res = super(MrpProduction, self.with_context(production=self)
                    )._action_compute_lines(properties=properties)
        # Assign work orders to each consume line
        for product_line in self.product_lines:
            product_line.work_order = self.workcenter_lines.filtered(
                lambda x: (x.routing_wc_line ==
                           product_line.bom_line.operation))
        return res

    @api.model
    def _make_production_consume_line(self, line):
        move_id = super(MrpProduction,
                        self)._make_production_consume_line(line)
        if line.work_order and move_id:
            move = self.env['stock.move'].browse(move_id)
            move.work_order = line.work_order.id
        return move_id

    @api.model
    def _make_consume_line_from_data(self, production, product, uom_id, qty,
                                     uos_id, uos_qty):
        move_id = super(MrpProduction, self)._make_consume_line_from_data(
            production, product, uom_id, qty, uos_id, uos_qty)
        work_order = self.env.context.get('default_work_order', False)
        if work_order:
            move = self.env['stock.move'].browse(move_id)
            move.work_order = work_order
        return move_id


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    bom_line = fields.Many2one(comodel_name="mrp.bom.line")
    work_order = fields.Many2one(
        comodel_name='mrp.production.workcenter.line', string='Work Order')


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    @api.multi
    @api.depends('move_lines', 'move_lines.state')
    def _compute_is_material_ready(self):
        for line in self:
            line.is_material_ready = (not any(
                x not in ('assigned', 'cancel', 'done') for x in
                line.mapped('move_lines.state'))
                if line.product_line else True)

    @api.multi
    @api.depends('routing_wc_line')
    def _compute_possible_workcenters(self):
        for line in self:
            line.possible_workcenters = line.mapped(
                'routing_wc_line.op_wc_lines.workcenter')

    product_line = fields.One2many(
        comodel_name='mrp.production.product.line', inverse_name='work_order',
        string='Product Lines')
    routing_wc_line = fields.Many2one(
        comodel_name='mrp.routing.workcenter', string='Routing WC Line')
    do_production = fields.Boolean(string='Produce here')
    time_start = fields.Float(string="Time Start")
    time_stop = fields.Float(string="Time Stop")
    move_lines = fields.One2many(
        comodel_name='stock.move', inverse_name='work_order', string='Moves')
    is_material_ready = fields.Boolean(
        string='Materials Ready', compute="_compute_is_material_ready")
    possible_workcenters = fields.Many2many(
        comodel_name="mrp.workcenter", compute="_compute_possible_workcenters")
    workcenter_id = fields.Many2one(
        domain="[('id', 'in', possible_workcenters[0][2])]")

    @api.one
    def action_assign(self):
        self.move_lines.action_assign()

    @api.one
    def force_assign(self):
        self.move_lines.force_assign()

    @api.model
    def create(self, vals):
        if vals.get('date_planned') and vals.get('production_id'):
            production = self.env['mrp.production'].browse(
                vals['production_id'])
            if vals['date_planned'] < production.date_planned:
                production.date_planned = vals['date_planned']
        return super(MrpProductionWorkcenterLine, self).create(vals)

    @api.multi
    def check_minor_sequence_operations(self):
        self.ensure_one()
        seq = self.sequence
        res = True
        for operation in self.production_id.workcenter_lines:
            if operation.sequence < seq and operation.state != 'done':
                res = False
                break
        return res

    def check_operation_moves_state(self, states):
        for move_line in self.move_lines:
            if move_line.state not in states:
                return False
        return True

    def action_start_working(self):
        for workorder in self:
            if workorder.routing_wc_line.previous_operations_finished and \
                    not workorder.check_minor_sequence_operations():
                raise exceptions.Warning(_("Previous operations not finished"))
            if not workorder.check_operation_moves_state(
                    ['assigned', 'cancel', 'done']):
                raise exceptions.Warning(
                    _("Missing materials to start the production"))
            if workorder.production_id.state in ('confirmed', 'ready'):
                workorder.production_id.signal_workflow('moves_ready')
                # bypass force_production method in production order
                workorder.production_id.state = 'in_production'
        return super(MrpProductionWorkcenterLine, self).action_start_working()

    @api.multi
    def button_done(self):
        res = {}
        move_list = self.move_lines.filtered(
            lambda x: x.state not in('cancel', 'done'))
        if move_list:
            idform = self.env.ref(
                'mrp_operations_extension.finish_wo_form_view')
            res = {
                'type': 'ir.actions.act_window',
                'name': _('Finish WO'),
                'res_model': 'workcenter.line.finish',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(idform.id, 'form')],
                'target': 'new',
                'context': self.env.context
                }
        else:
            self.signal_workflow('button_done')
        return res
