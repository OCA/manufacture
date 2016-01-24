# -*- coding: utf-8 -*-
# © 2014-2015 Avanzosc
# © 2014-2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models
from openerp.tools.translate import _


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_done(self):
        task_obj = self.env['project.task']
        analytic_line_obj = self.env['account.analytic.line']
        result = super(StockMove, self).action_done()
        records = self.filtered(lambda x: (x.raw_material_production_id and
                                           x.product_id.standard_price))
        for record in records:
            journal_id = self.env.ref('mrp.analytic_journal_materials', False)
            production = record.raw_material_production_id
            name = "-".join([
                production.name or '',
                record.work_order.workcenter_id.code or '',
                record.work_order.routing_wc_line.routing_id.code or '',
                record.product_id.default_code or '',
                _('MAT')])
            analytic_vals = (production._prepare_real_cost_analytic_line(
                journal_id, name, production, record.product_id,
                workorder=record.work_order, qty=record.product_qty,
                amount=(-record.product_id.standard_price *
                        record.product_qty)))
            task = task_obj.search([('mrp_production_id', '=', production.id),
                                    ('workorder', '=', False)])
            analytic_vals['task_id'] = task and task[0].id or False
            analytic_line_obj.create(analytic_vals)
        return result

    @api.multi
    def product_price_update_production_done(self):
        records = self.filtered(
            lambda x: (x.production_id and
                       x.product_id.cost_method == 'average'))
        for move in records:
            prod_total_cost = move.production_id.real_cost
            product = move.product_id
            product_avail = product.qty_available
            amount_unit = product.standard_price
            tmpl_available = product.product_tmpl_id.qty_available
            tmpl_price = product.product_tmpl_id.standard_price
            if move.state == 'done':
                product_avail -= move.product_qty
                tmpl_available -= move.product_qty
            new_product_price = (
                (amount_unit * product_avail + prod_total_cost) /
                ((product_avail >= 0.0 and product_avail or 0.0) +
                 move.product_qty))
            new_tmpl_price = ((tmpl_price * tmpl_available + prod_total_cost) /
                              ((tmpl_available > 0.0 and tmpl_available or
                                0.0) + move.product_qty))
            product.sudo().standard_price = new_product_price
            product.sudo().product_tmpl_id.standard_price = new_tmpl_price

    @api.model
    def get_price_unit(self, move):
        if move.production_id:
            return move.production_id.real_cost / move.product_qty
        else:
            return super(StockMove, self).get_price_unit(move)
