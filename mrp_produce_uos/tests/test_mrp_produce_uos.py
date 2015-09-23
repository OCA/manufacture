# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestMrpProduceUos(TransactionCase):

    def setUp(self):
        super(TestMrpProduceUos, self).setUp()
        self.product_model = self.env['product.product']
        self.bom_model = self.env['mrp.bom']
        self.production_model = self.env['mrp.production']
        self.wizard_model = self.env['mrp.product.produce']

        self.product_a = self.product_model.create({
            'name': 'Product A',
            'list_price': 30,
            'uom_id': self.env.ref('product.product_uom_meter').id,
            'uom_po_id': self.env.ref('product.product_uom_meter').id,
            'uos_id': self.env.ref('product.product_uom_unit').id,
        })

        self.product_b = self.product_model.create({
            'name': 'Product B',
            'standard_price': 10,
        })

        self.bom = self.bom_model.create({
            'product_tmpl_id': self.product_a.product_tmpl_id.id,
            'product_qty': 1,
            'product_uom': self.env.ref('product.product_uom_meter').id,
            'bom_line_ids': [
                (0, 0, {
                    'product_id': self.product_b.id,
                    'product_qty': 2,
                }),
            ],
        })

    def prepare_production(self):
        self.production = self.production_model.create({
            'product_id': self.product_a.id,
            'product_qty': 0.5,
            'product_uos_qty': 1,
            'bom_id': self.bom.id,
            'product_uom': self.product_a.uom_id.id,
            'product_uos': self.product_a.uos_id.id,
        })
        self.wizard = self.wizard_model.with_context(
            {'active_id': self.production.id}).create({
                'product_id': self.product_a.id,
            })

    def produce(self):
        self.production.action_confirm()
        self.wizard.product_uos_qty = 0.5
        self.wizard._onchange_product_uos_qty()
        self.production_model.action_produce(
            self.production.id, self.wizard.product_qty,
            'consume_produce', self.wizard)
        self.production.refresh()
        self.assertEqual(
            len(self.production.move_created_ids2), 1)
        self.move_produced = self.production.move_created_ids2[0]

        self.assertEqual(self.move_produced.product_uom_qty, 0.25)
        self.assertEqual(self.move_produced.product_uos_qty, 0.5)

        self.assertEqual(
            len(self.production.move_created_ids), 1)
        self.move_to_produce = self.production.move_created_ids[0]

        self.assertEqual(self.move_to_produce.product_uom_qty, 0.25)
        self.assertEqual(self.move_to_produce.product_uos_qty, 0.5)

    def test_action_produce(self):
        self.prepare_production()
        self.produce()
