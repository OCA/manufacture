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
import openerp.addons.decimal_precision as dp


class QcTest(orm.Model):
    _inherit = 'qc.test'

    def _get_categ(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for test in self.browse(cr, uid, ids):
            if test.product_id:
                if test.product_id.categ_id:
                    res[test.id] = test.product_id.categ_id.id
                else:
                    res[test.id] = False
            else:
                res[test.id] = False
        return res

    def _update_vals(self, cr, uid, vals, context=None):
        if 'picking_id' in vals and vals['picking_id']:
            if 'object_id' not in vals:
                vals.update({'object_id': 'stock.picking,' +
                             str(vals['picking_id'])})
        if 'production_id' in vals and vals['production_id']:
            if 'object_id' not in vals:
                vals.update({'object_id': 'mrp.production,' +
                             str(vals['production_id'])})
        if 'stock_move_id' in vals and vals['stock_move_id']:
            if 'object_id' not in vals:
                vals.update({'object_id': 'stock.move,' +
                             str(vals['stock_move_id'])})
        if 'object_id' in vals and vals['object_id']:
            ref = vals['object_id'].split(',')
            model = ref[0]
            res_id = int(ref[1])
            if model == 'product.product' and 'product_id' not in vals:
                vals.update({'product_id': res_id,
                             'production_id': False,
                             'stock_move_id': False,
                             'picking_id': False})
            elif model == 'mrp.production' and 'production_id' not in vals:
                mrp_obj = self.pool['mrp.production']
                mrp = mrp_obj.read(cr, uid, res_id, ['product_id'],
                                   context=context)
                vals.update({'production_id': res_id,
                             'product_id': mrp['product_id'][0],
                             'stock_move_id': False,
                             'picking_id': False})
            elif model == 'stock.move' and 'stock_move_id' not in vals:
                move_obj = self.pool['stock.move']
                move = move_obj.read(cr, uid, res_id, ['product_id',
                                                       'picking_id',
                                                       'restrict_lot_id',
                                                       'production_id'],
                                     context=context)
                vals.update({'stock_move_id': res_id,
                             'product_id': (move['product_id'] and
                                            move['product_id'][0]),
                             'picking_id': (move['picking_id'] and
                                            move['picking_id'][0]),
                             'lot_id': (move['restrict_lot_id'] and
                                        move['restrict_lot_id'][0]),
                             'production_id': (move['production_id'] and
                                               move['production_id'][0])})
        return vals

    _columns = {
        'product_qty': fields.float('Quantity',
                                    digits_compute=dp.get_precision(
                                        'Product UoM')),
        'origin': fields.char('Origin', size=128),
        'stock_move_id': fields.many2one('stock.move', 'Stock Move',
                                         ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product'),
        'categ_id': fields.function(_get_categ, type='many2one',
                                    relation='product.category',
                                    string='Category', store=True),
        'picking_id': fields.many2one('stock.picking', 'Picking'),
        'lot_id': fields.many2one('stock.production.lot', 'Lot'),
        'production_id': fields.many2one('mrp.production', 'Production'),
    }

    def create(self, cr, uid, vals, context=None):
        vals = self._update_vals(cr, uid, vals, context=context)
        return super(QcTest, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        vals = self._update_vals(cr, uid, vals, context=context)
        result = super(QcTest, self).write(cr, uid, ids, vals, context=context)
        move_obj = self.pool['stock.move']
        if ids:
            if not isinstance(ids, list):
                ids = [ids]
            for test in self.browse(cr, uid, ids):
                if test.stock_move_id:
                    move_obj.write(cr, uid, [test.stock_move_id.id], {},
                                   context=context)
        return result

    def onchange_product(self, cr, uid, ids, product_id, context=None):
        res = {'categ_id': False}
        product_obj = self.pool['product.product']
        if product_id:
            product = product_obj.browse(cr, uid, product_id, context=context)
            if product.categ_id:
                res.update({'categ_id': product.categ_id.id})
        return {'value': res}

    def button_create_test_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_obj = self.pool['stock.move']
        template_obj = self.pool['qc.test.template']
        test_line_obj = self.pool['qc.test.line']
        if ids:
            for test in self.browse(cr, uid, ids, context=context):
                if test.test_template_id:
                    how_many = move_obj._how_many_test_create(
                        cr, uid, test.product_id, test.product_qty,
                        context=context)
                    if how_many > 0:
                        max_sequence = 0
                        if test.test_line_ids:
                            for line in test.test_line_ids:
                                if line.sequence > max_sequence:
                                    max_sequence = line.sequence
                        template = template_obj.browse(
                            cr, uid, test.test_template_id.id, context=context)
                        # Creo las líneas del test
                        if template.test_template_line_ids:
                            count = 0
                            howmany = how_many
                            while howmany > 0:
                                count = count + 1
                                for line in template.test_template_line_ids:
                                    sequence = max_sequence + count
                                    data = {
                                        'sequence': sequence,
                                        'test_id': test.id,
                                        'test_template_line_id': line.id,
                                        'min_value': line.min_value,
                                        'max_value': line.max_value
                                    }
                                    if line.uom_id:
                                        data.update({'uom_id': line.uom_id.id})
                                    if line.proof_id:
                                        data.update({'proof_id':
                                                     line.proof_id.id})
                                    if line.method_id:
                                        data.update({'method_id':
                                                     line.method_id.id})
                                    if line.type:
                                        data.update({'proof_type':
                                                     line.type})
                                    test_line_obj.create(cr, uid, data,
                                                         context=context)
                                howmany -= 1
        return True


class QcTestLine(orm.Model):
    _inherit = 'qc.test.line'
    _order = 'sequence'

    _columns = {
        'sequence': fields.integer('Sequence', readonly=True),
    }

    def create(self, cr, uid, data, context=None):
        if 'sequence' not in data:
            data.update({'sequence': 1})
        picking_obj = self.pool['stock.picking']
        production_obj = self.pool['mrp.production']
        new_id = super(QcTestLine, self).create(cr, uid, data, context=context)
        line = self.browse(cr, uid, new_id, context=context)
        if line.test_id:
            if line.test_id.picking_id:
                picking_obj.write(
                    cr, uid, [line.test_id.picking_id.id], {}, context=context)
            if line.test_id.production_id:
                production_obj.write(
                    cr, uid, [line.test_id.production_id.id], {},
                    context=context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        picking_obj = self.pool['stock.picking']
        production_obj = self.pool['mrp.production']
        result = super(QcTestLine, self).write(cr, uid, ids, vals,
                                               context=context)
        if ids:
            for line in self.browse(cr, uid, ids, context=context):
                if line.test_id:
                    if line.test_id.picking_id:
                        picking_obj.write(
                            cr, uid, [line.test_id.picking_id.id], {},
                            context=context)
                    if line.test_id.production_id:
                        production_obj.write(
                            cr, uid, [line.test_id.production_id.id], {},
                            context=context)
        return result


class QcTestTemplate(orm.Model):
    _inherit = 'qc.test.template'

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'product_category_id': fields.many2one('product.category',
                                               'Product Category'),
        'picking_type_ids': fields.many2many('stock.picking.type',
                                             'rel_qc_template_picking_type',
                                             'template_id', 'type_id',
                                             'Picking Types')
    }
