# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Advanced Open Source Consulting
#    Copyright (C) 2011 - 2013 Avanzosc <http://www.avanzosc.com>
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


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

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
        # Tests asociados a la OF
        'qc_test_ids': fields.one2many('qc.test', 'production_id', 'Tests'),
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

    def action_confirm(self, cr, uid, ids, context=None):
        move_obj = self.pool['stock.move']
        test_obj = self.pool['qc.test']
        result = super(MrpProduction, self).action_confirm(cr, uid, ids,
                                                           context=context)
        for production in self.browse(cr, uid, ids, context=context):
            if production.move_created_ids:
                for move in production.move_created_ids:
                    how_many = move_obj._how_many_test_create(
                        cr, uid, move.product_id, move.product_qty,
                        context=context)
                    if how_many > 0:
                        move_obj._create_test_automatically(
                            cr, uid, how_many, move, context=context)
                        production2 = self.browse(cr, uid, production.id,
                                                  context=context)
                        if production2.qc_test_ids:
                            for test in production2.qc_test_ids:
                                test_obj.write(cr, uid, [test.id],
                                               {'stock_move_id': False},
                                               context=context)
        return result
