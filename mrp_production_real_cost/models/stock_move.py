# -*- coding: utf-8 -*-
# © 2014-2015 Avanzosc
# © 2014-2015 Pedro M. Baeza
# © 2016 Antiun Ingenieria S.L. - Antonio Espinosa
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

    def _new_average_price(self, data):
        current_price = data.get('price', 0.0)
        current_available = data.get('available', 0.0)
        moved = data.get('moved', 0.0)
        cost = data.get('cost', 0.0)
        if current_available < 0:
            current_available = 0.0
        current_value = current_available * current_price
        if (current_available + moved) <= 0:
            return 0.0
        return (
            (current_value + cost) /
            (current_available + moved)
        )

    @api.multi
    def product_price_update_production_done(self):
        records = self.filtered(
            lambda x: (x.production_id and
                       x.product_id.cost_method == 'average'))
        products = {}
        for move in records:
            product = move.product_id
            product_data = products.get(product.id, False) or {}
            if not product_data:
                product_data['product'] = product
                product_data['available'] = product.qty_available
                product_data['price'] = product.standard_price
                product_data['moved'] = 0.0
                product_data['cost'] = move.production_id.real_cost
            if move.state == 'done':
                product_data['available'] -= move.product_qty
                product_data['moved'] += move.product_qty
            products[product.id] = product_data
        for product_id, product_data in products.iteritems():
            new_price = self._new_average_price(product_data)
            product_data['product'].sudo().standard_price = new_price

    @api.model
    def get_price_unit(self, move):
        if move.production_id:
            return move.production_id.real_cost / move.product_qty
        else:
            return super(StockMove, self).get_price_unit(move)
