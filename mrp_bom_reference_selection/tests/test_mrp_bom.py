# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp.tests import common


class test_mrp_bom(common.TransactionCase):

    def get_bom_ref(self, code, product):
        return self.ref_model.search([
            ('bom_id.product_tmpl_id', '=', product.product_tmpl_id.id),
            ('name', '=', code),
        ])[0]

    def setUp(self):
        super(test_mrp_bom, self).setUp()

        self.ref_model = self.env['mrp.bom.reference']
        self.product_model = self.env['product.product']
        self.bom_model = self.env['mrp.bom']
        self.route = self.env.ref('mrp.route_warehouse0_manufacture')
        self.production_model = self.env['mrp.production']
        self.lot_model = self.env['stock.production.lot']
        self.wizard_model = self.env['mrp.product.produce']

        self.product_a = self.product_model.create({
            'name': 'Product A',
            'route_ids': [(4, self.route.id)],
            'standard_price': 10,
        })

        self.product_b = self.product_model.create({
            'name': 'Product B',
            'route_ids': [(4, self.route.id)],
            'standard_price': 20,
        })

        self.product_c = self.product_model.create({
            'name': 'Product C',
            'route_ids': [(4, self.route.id)],
            'standard_price': 30,
        })

        self.product_d = self.product_model.create({
            'name': 'Product C',
            'route_ids': [(4, self.route.id)],
            'standard_price': 30,
        })

        self.bom_a1 = self.bom_model.create({
            'product_tmpl_id': self.product_a.product_tmpl_id.id,
            'product_qty': 1,
            'code': 'A-1',
        })

        self.bom_a2 = self.bom_model.create({
            'product_tmpl_id': self.product_a.product_tmpl_id.id,
            'product_qty': 1,
            'code': 'A-2',
        })

        self.bom_b1 = self.bom_model.create({
            'product_tmpl_id': self.product_b.product_tmpl_id.id,
            'product_qty': 1,
            'code': 'B-1',
            'bom_line_ids': [(0, 0, {
                'product_id': self.product_a.id,
                'reference_id': self.get_bom_ref('A-1', self.product_a).id,
                'product_qty': 1,
            })],
        })

        self.bom_b2 = self.bom_model.create({
            'product_tmpl_id': self.product_b.product_tmpl_id.id,
            'product_qty': 1,
            'code': 'B-2',
            'bom_line_ids': [(0, 0, {
                'product_id': self.product_a.id,
                'reference_id': self.get_bom_ref('A-2', self.product_a).id,
                'product_qty': 1,
            })],
        })

        self.bom_c1 = self.bom_model.create({
            'product_tmpl_id': self.product_c.product_tmpl_id.id,
            'product_qty': 1,
            'code': 'C-1',
            'bom_line_ids': [
                (0, 0, {
                    'product_id': self.product_a.id,
                    'reference_id': self.get_bom_ref('A-1', self.product_a).id,
                    'product_qty': 2,
                    'sequence': 1,
                }),
                (0, 0, {
                    'product_id': self.product_b.id,
                    'reference_id': self.get_bom_ref('B-2', self.product_b).id,
                    'product_qty': 1,
                    'sequence': 2,
                })
            ],
        })

        self.bom_c2 = self.bom_model.create({
            'product_tmpl_id': self.product_c.product_tmpl_id.id,
            'product_qty': 1,
            'code': 'C-2',
            'bom_line_ids': [
                (0, 0, {
                    'product_id': self.product_a.id,
                    'reference_id': self.get_bom_ref('A-2', self.product_a).id,
                    'product_qty': 2,
                    'sequence': 1,
                }),
                (0, 0, {
                    'product_id': self.product_b.id,
                    'reference_id': self.get_bom_ref('B-1', self.product_b).id,
                    'product_qty': 1,
                    'sequence': 2,
                })
            ],
        })

        self.bom_d1 = self.bom_model.create({
            'product_tmpl_id': self.product_d.product_tmpl_id.id,
            'product_qty': 1,
            'code': 'D-1',
            'bom_line_ids': [
                (0, 0, {
                    'product_id': self.product_b.id,
                    'reference_id': self.get_bom_ref('B-1', self.product_b).id,
                    'product_qty': 2,
                    'sequence': 1,
                }),
                (0, 0, {
                    'product_id': self.product_c.id,
                    'reference_id': self.get_bom_ref('C-2', self.product_c).id,
                    'product_qty': 2,
                    'sequence': 2,
                }),
                (0, 0, {
                    'product_id': self.product_a.id,
                    'reference_id': self.get_bom_ref('A-2', self.product_a).id,
                    'product_qty': 3,
                    'sequence': 3,
                }),
            ],
        })

    def get_bom_line(self, bom, ref):
        for line in bom.bom_line_ids:
            if line.reference_id == ref:
                return line
        return False

    def test_bom_child_line_ids(self):
        """
        Test the child_line_ids field when the child bom has one bom lines
        """
        line_d1_b1 = self.get_bom_line(
            self.bom_d1, self.get_bom_ref('B-1', self.product_b))

        line_b1_a1 = self.get_bom_line(
            self.bom_b1, self.get_bom_ref('A-1', self.product_a))

        self.assertEqual(len(line_d1_b1.child_line_ids), 1)

        self.assertEqual(line_d1_b1.child_line_ids[0], line_b1_a1)

    def test_bom_child_line_ids_with_2_childs(self):
        """
        Test the child_line_ids field when the child bom has 2 bom lines
        """
        line_d1_c2 = self.get_bom_line(
            self.bom_d1, self.get_bom_ref('C-2', self.product_c))

        line_c2_a2 = self.get_bom_line(
            self.bom_c2, self.get_bom_ref('A-2', self.product_a))

        line_c2_b1 = self.get_bom_line(
            self.bom_c2, self.get_bom_ref('B-1', self.product_b))

        self.assertEqual(len(line_d1_c2.child_line_ids), 2)

        self.assertEqual(line_d1_c2.child_line_ids[0], line_c2_a2)
        self.assertEqual(line_d1_c2.child_line_ids[1], line_c2_b1)

    def test_bom_child_ids_change_child(self):
        """
        Test the child_line_ids field when a child is changed
        """
        line_d1_c2 = self.get_bom_line(
            self.bom_d1, self.get_bom_ref('C-2', self.product_c))

        self.bom_c2.bom_line_ids[0].unlink()

        self.bom_c2.write({
            'bom_line_ids': [
                (0, 0, {
                    'product_id': self.product_a.id,
                    'reference_id': self.get_bom_ref('A-1', self.product_a).id,
                    'product_qty': 1,
                    'sequence': 3,
                }),
            ]})

        line_c2_b1 = self.get_bom_line(
            self.bom_c2, self.get_bom_ref('B-1', self.product_b))

        line_c2_a1 = self.get_bom_line(
            self.bom_c2, self.get_bom_ref('A-1', self.product_a))

        self.assertEqual(len(line_d1_c2.child_line_ids), 2)
        self.assertEqual(line_d1_c2.child_line_ids[0], line_c2_b1)
        self.assertEqual(line_d1_c2.child_line_ids[1], line_c2_a1)

    def prepare_production(self):
        self.production = self.production_model.create({
            'product_id': self.product_d.id,
            'product_qty': 1,
            'bom_id': self.bom_d1.id,
            'product_uom': self.product_d.uom_id.id
        })

        self.lot = self.lot_model.create({
            'product_id': self.product_d.id,
        })

        self.wizard = self.wizard_model.create({
            'product_id': self.product_d.id,
            'product_qty': 1,
            'lot_id': self.lot.id,
        })

    def produce(self):
        self.production.action_confirm()
        self.production_model.action_produce(
            self.production.id, 1, 'consume_produce', self.wizard)
        self.production.refresh()

        self.assertEqual(
            len(self.production.move_created_ids2), 1)

        self.move_produced = self.production.move_created_ids2[0]

        self.assertEqual(
            len(self.move_produced.lot_ids), 1)

        self.lot_produced = self.move_produced.lot_ids

    def test_action_produce(self):
        """
        Test that the bom_id field is computed in a lot produced
        """
        self.prepare_production()
        self.produce()
        self.assertEqual(self.lot_produced.bom_id, self.bom_d1)
