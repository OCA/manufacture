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

from openerp.osv import orm, fields
from openerp.tools.translate import _
# import time


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def _how_many_test_create(self, cr, uid, product, qty, context=None):
        rank_obj = self.pool['sample.rank']
        how_many = 0
        rank_ids = rank_obj.search(cr, uid, [('product_id', '=', product.id),
                                             ('category_id', '=', False)],
                                   limit=1, context=context)
        if not rank_ids:
            rank_ids = rank_obj.search(
                cr, uid, [('product_id', '=', False),
                          ('category_id', '=', product.categ_id.id)], limit=1,
                context=context)
        if not rank_ids:
            rank_ids = rank_obj.search(cr, uid, [('product_id', '=', False),
                                                 ('category_id', '=', False)],
                                       limit=1, context=context)
        if rank_ids:
            rank = rank_obj.browse(cr, uid, rank_ids[0], context=context)
            if rank.sample_rank_lines_ids:
                for line in rank.sample_rank_lines_ids:
                    if qty >= line.min and qty <= line.max:
                        how_many = line.how_many
        return how_many

    def _create_test_automatically(self, cr, uid, how_many, move,
                                   context=None):
        template_obj = self.pool['qc.test.template']
        test_obj = self.pool['qc.test']
        test_line_obj = self.pool['qc.test.line']
        template_ids = template_obj.search(
            cr, uid, [('product_id', '=', move.product_id.id),
                      ('active', '=', True)], context=context)
        if not template_ids:
            template_ids = template_obj.search(
                cr, uid,
                [('product_category_id', '=', move.product_id.categ_id.id),
                 ('product_id', '=', False),
                 ('active', '=', True)], context=context)
        if not template_ids:
            template_ids = template_obj.search(
                cr, uid, [('product_category_id', '=', False),
                          ('product_id', '=', False),
                          ('active', '=', True)], context=context)
        if not template_ids:
            raise orm.except_orm(
                _('Test Creation Error !'),
                _('No test template found for product: %s, category: %s') %
                (move.product_id.name, move.product_id.categ_id.name))
        else:
            for template in template_obj.browse(cr, uid, template_ids,
                                                context=context):
                # Creo la cabecera del test
                if move.picking_id:
                    origin = (str(move.picking_id.name) + ' - ' +
                              move.product_id.name)
                elif move.production_id:
                    origin = (str(move.production_id.name) + ' - ' +
                              move.product_id.name)
                data = {
                    # 'name': time.strftime('%Y%m%d %H%M%S'),
                    'test_template_id': template.id,
                    'origin': origin,
                    'enabled': True,
                    'product_id': move.product_id.id,
                    'state': 'draft',
                    'product_qty': move.product_qty,
                    'stock_move_id': move.id,
                    'lot_id': move.lot_ids and move.lot_ids.id,
                    'picking_id': move.picking_id and move.picking_id.id,
                    'production_id': (move.production_id and
                                      move.production_id.id),
                }
                test_id = test_obj.create(cr, uid, data, context=context)
                # Creo las líneas del test
                if template.test_template_line_ids:
                    count = 0
                    howmany = how_many
                    while howmany > 0:
                        count = count + 1
                        for line in template.test_template_line_ids:
                            data = {
                                'sequence': count,
                                'test_id': test_id,
                                'test_template_line_id': line.id,
                                'min_value': line.min_value,
                                'max_value': line.max_value,
                                'uom_id': line.uom_id and line.uom_id.id,
                                'proof_id': line.proof_id and line.proof_id.id,
                                'method_id': (line.method_id and
                                              line.method_id.id),
                                'proof_type': line.type,
                            }
                            if line.type:
                                if (line.type == 'qualitative' and
                                        line.valid_value_ids):
                                    my_data = []
                                    for val in line.valid_value_ids:
                                        my_data.append(val.id)
                                    if my_data:
                                        data.update({'valid_value_ids':
                                                     [(6, 0, my_data)]})
                            test_line_obj.create(cr, uid, data,
                                                 context=context)
                        howmany -= 1
        return True


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def _count_tests(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for test in self.browse(cr, uid, ids, context=context):
            created = 0
            done = 0
            passed = 0
            failed = 0
            if test.qc_test_ids:
                for line in test.qc_test_ids:
                    created += 1
                    if line.state not in ('draft', 'waiting'):
                        done += 1
                        if line.state == 'success':
                            passed += 1
                        elif line.state == 'failed':
                            failed += 1
            res[test.id] = {
                'created_tests': created,
                'done_tests': done,
                'passed_tests': passed,
                'failed_tests': failed,
            }
        return res

    _columns = {
        # Test asociados al albaran
        'qc_test_ids': fields.one2many('qc.test', 'picking_id', 'Tests'),
        # Numero de test creados
        'created_tests': fields.function(_count_tests, string="Created Tests",
                                         type="integer", multi="test_count"),
        # Numero de test realizados
        'done_tests': fields.function(_count_tests, string="Realized Tests",
                                      type="integer", multi="test_count"),
        # Numero de test OK
        'passed_tests': fields.function(_count_tests, string="Tests OK",
                                        type="integer", multi="test_count"),
        # Numero de test fallados
        'failed_tests': fields.function(_count_tests, string="Tests no OK",
                                        type="integer", multi="test_count"),
    }

    # @api.cr_uid_ids_context  # this is taken from stock module
    def do_transfer(self, cr, uid, ids, context=None):
        do_transfer = super(StockPicking, self).do_transfer(cr, uid, ids,
                                                            context=context)
        if do_transfer:
            for picking in self.browse(cr, uid, ids, context=context):
                if (picking.state == 'done' and
                        picking.picking_type_id.code == 'incoming' and
                        picking.move_lines):
                    move_obj = self.pool['stock.move']
                    for move in picking.move_lines:
                        how_many = move_obj._how_many_test_create(
                            cr, uid, move.product_id, move.product_qty,
                            context=context)
                        if how_many > 0:
                            move_obj._create_test_automatically(
                                cr, uid, how_many, move, context=context)
        return do_transfer


class StockProductionLot(orm.Model):
    _inherit = 'stock.production.lot'

    def _count_tests(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for test in self.browse(cr, uid, ids, context=context):
            created = 0
            done = 0
            passed = 0
            failed = 0
            if test.qc_test_ids:
                for line in test.qc_test_ids:
                    created += 1
                    if line.state not in ('draft', 'waiting'):
                        done += 1
                        if line.state == 'success':
                            passed += 1
                        elif line.state == 'failed':
                            failed += 1
            res[test.id] = {
                'created_tests': created,
                'done_tests': done,
                'passed_tests': passed,
                'failed_tests': failed,
            }
        return res

    _columns = {
        # Test asociados al albaran
        'qc_test_ids': fields.one2many('qc.test', 'lot_id', 'Tests'),
        # Numero de test creados
        'created_tests': fields.function(_count_tests, string="Created Tests",
                                         type="integer", multi="test_count"),
        # Numero de test realizados
        'done_tests': fields.function(_count_tests, string="Realized Tests",
                                      type="integer", multi="test_count"),
        # Numero de test OK
        'passed_tests': fields.function(_count_tests, string="Tests OK",
                                        type="integer", multi="test_count"),
        # Numero de test fallados
        'failed_tests': fields.function(_count_tests, string="Tests no OK",
                                        type="integer", multi="test_count"),
    }
