# -*- encoding: utf-8 -*-
##############################################################################
#
#    @authors: Alexander Ezquevo <alexander@acysos.com>
#    Copyright (C) 2015  Acysos S.L.
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class Lot(models.Model):
    _inherit = 'stock.production.lot'

    unit_cost = fields.Float(string='Lot unit cost')


class MRP_production(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_produce(
            self, production_qty, production_mode,
            wiz=False):
        if wiz and wiz.lot_id and len(wiz.consume_lines) > 0:
            control = True
            for line in wiz.consume_lines:
                if not line.lot_id:
                    control = False
            if(control):
                self.calculateCost(wiz)
        super(MRP_production, self).action_produce(
            self.id, production_qty, production_mode, wiz)

    @api.one
    def calculateCost(self, wiz):
        stock_quant_obj = self.env['stock.quant']
        totalCost = 0.0
        for line in wiz.consume_lines:
            moves = stock_quant_obj.search([
                ('product_id', '=', line.product_id.id,),
                ('lot_id', '=', line.lot_id.id)])
            qty = 0.0
            amount = 0.0
            for move in moves:
                qty += move.qty
                amount += move.cost * move.qty
            unit_price = amount/qty
            totalCost += line.product_qty * unit_price
        if wiz.lot_id.unit_cost:
            initial_lots = stock_quant_obj.search([
                ('lot_id', '=', wiz.lot_id.id)])
            initial_totalCost = 0.0
            totalQty = 0.0
            for q in initial_lots:
                initial_totalCost += wiz.lot_id.unit_cost * q.qty
                totalQty += q.qty
            totalQty += wiz.product_qty
            totalCost = initial_totalCost + totalCost
            wiz.lot_id.unit_cost = totalCost/totalQty
        else:
            wiz.lot_id.unit_cost = totalCost/wiz.product_qty
