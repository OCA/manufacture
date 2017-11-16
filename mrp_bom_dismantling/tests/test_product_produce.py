# -*- coding: utf8 -*-

from openerp.tests import TransactionCase


class TestProductProduce(TransactionCase):

    def setUp(self):
        super(TestProductProduce, self).setUp()

        self.produce_model = self.env['mrp.product.produce']
        product_model = self.env['product.product']
        self.lot_model = self.env['stock.production.lot']

        unit_uom = self.browse_ref('product.product_uom_unit')

        wh_main = self.browse_ref('stock.warehouse0')

        # Create simple bom with by products
        self.p1 = product_model.create({'name': 'Test p1'})
        self.p2 = product_model.create({'name': 'Test p2'})
        self.p3 = product_model.create({'name': 'Test p3'})

        # We have 1 self.p2 in stock
        inventory = self.env['stock.inventory'].create({
            'name': 'self.p2 inventory',
            'location_id': wh_main.lot_stock_id.id,
            'filter': 'partial'
        })
        inventory.prepare_inventory()

        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': self.p2.id,
            'location_id': wh_main.lot_stock_id.id,
            'product_qty': 1
        })
        inventory.action_done()

        # self.p1 need self.p2 and generates one byproduct self.p3
        bom = self.env['mrp.bom'].create({
            'product_tmpl_id': self.p1.product_tmpl_id.id,
            'product_id': self.p1.id,
            'product_qty': 1,
            'product_uom': unit_uom.id,
        })

        self.env['mrp.bom.line'].create({
            'bom_id': bom.id,
            'product_id': self.p2.id,
            'product_qty': 1,
            'product_uom': unit_uom.id,
        })

        self.env['mrp.subproduct'].create({
            'bom_id': bom.id,
            'product_id': self.p3.id,
            'product_qty': 1,
            'product_uom': unit_uom.id,
        })

        # Create MRP Order
        self.mrp_order_id = bom.create_mrp_production()['res_id']
        self.mrp_order = self.env['mrp.production'].browse(self.mrp_order_id)
        self.mrp_order.action_confirm()
        self.mrp_order.action_assign()

    def test_produced_products_lots(self):
        # Wizard simulation
        wizard = self.produce_model.with_context(
            active_id=self.mrp_order_id
        ).create({})
        wizard.on_change_product_id()
        self.assertEqual(2, len(wizard.move_lot_ids))
        self.assertEqual(
            [self.p1, self.p3], [x.product_id for x in wizard.move_lot_ids]
        )

        lot_p1 = self.lot_model.create(
            {'name': 'LOT_01', 'product_id': self.p1.id}
        )
        wizard.move_lot_ids[0].lot_id = lot_p1

        lot_p3 = self.lot_model.create(
            {'name': 'LOT_03', 'product_id': self.p3.id}
        )
        wizard.move_lot_ids[1].lot_id = lot_p3

        wizard.do_produce()

        # Check created move in mrp.production
        self.mrp_order.refresh()
        self.assertEqual(lot_p1,
                         self.mrp_order.move_created_ids2[0].restrict_lot_id)
        self.assertEqual(lot_p3,
                         self.mrp_order.move_created_ids2[1].restrict_lot_id)

        # Check stock.quants
        quant_model = self.env['stock.quant']

        p1_quants = quant_model.search([('product_id', '=', self.p1.id)])
        self.assertEqual(1, len(p1_quants))
        self.assertEqual(lot_p1, p1_quants.lot_id)
        self.assertEqual(1, p1_quants.qty)

        p3_quants = quant_model.search([('product_id', '=', self.p3.id)])
        self.assertEqual(1, len(p3_quants))
        self.assertEqual(1, p3_quants.qty)

    def test_tracking_lot(self):
        wizard = self.produce_model.with_context(
            active_id=self.mrp_order_id
        ).create({})
        wizard.on_change_product_id()

        self.assertEqual(False, wizard.move_lot_ids[0].lot_required)
        self.assertEqual(False, wizard.move_lot_ids[1].lot_required)

        self.p1.tracking = 'serial'
        self.p1.refresh()

        self.assertEqual(True, wizard.move_lot_ids[0].lot_required)
        self.assertEqual(False, wizard.move_lot_ids[1].lot_required)

        self.p3.tracking = 'lot'
        self.p3.refresh()

        self.assertEqual(True, wizard.move_lot_ids[0].lot_required)
        self.assertEqual(True, wizard.move_lot_ids[1].lot_required)

        wizard.mode = 'consume'
        wizard.refresh()
        self.assertEqual(False, wizard.move_lot_ids[0].lot_required)
        self.assertEqual(False, wizard.move_lot_ids[1].lot_required)
