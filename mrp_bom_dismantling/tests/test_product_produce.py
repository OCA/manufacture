# -*- coding: utf8 -*-

from openerp.tests import TransactionCase


class TestProductProduce(TransactionCase):

    def test_produced_products_lots(self):
        produce_model = self.env['mrp.product.produce']
        product_model = self.env['product.product']
        lot_model = self.env['stock.production.lot']
        quant_model = self.env['stock.quant']

        unit_uom = self.browse_ref('product.product_uom_unit')

        wh_main = self.browse_ref('stock.warehouse0')

        # Create simple bom with by products
        p1 = product_model.create({'name': 'Test P1'})
        p2 = product_model.create({'name': 'Test P2'})
        p3 = product_model.create({'name': 'Test P3'})

        # We have 1 P2 in stock
        inventory = self.env['stock.inventory'].create({
            'name': 'P2 inventory',
            'location_id': wh_main.lot_stock_id.id,
            'filter': 'partial'
        })
        inventory.prepare_inventory()

        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': p2.id,
            'location_id': wh_main.lot_stock_id.id,
            'product_qty': 1
        })
        inventory.action_done()

        # P1 need P2 and generates one byproduct P3
        bom = self.env['mrp.bom'].create({
            'product_tmpl_id': p1.product_tmpl_id.id,
            'product_id': p1.id,
            'product_qty': 1,
            'product_uom': unit_uom.id,
        })

        self.env['mrp.bom.line'].create({
            'bom_id': bom.id,
            'product_id': p2.id,
            'product_qty': 1,
            'product_uom': unit_uom.id,
        })

        self.env['mrp.subproduct'].create({
            'bom_id': bom.id,
            'product_id': p3.id,
            'product_qty': 1,
            'product_uom': unit_uom.id,
        })

        # Create MRP Order
        mrp_order_id = bom.create_mrp_production()['res_id']
        mrp_order = self.env['mrp.production'].browse(mrp_order_id)
        mrp_order.action_confirm()
        mrp_order.action_assign()

        # Wizard simulation
        wizard = produce_model.with_context(active_id=mrp_order_id).create({})
        wizard.on_change_product_id()
        self.assertEqual(2, len(wizard.move_lot_ids))
        self.assertEqual([p1, p3], [x.product_id for x in wizard.move_lot_ids])

        lot_p1 = lot_model.create({'name': 'LOT_01', 'product_id': p1.id})
        wizard.move_lot_ids[0].lot_id = lot_p1

        lot_p3 = lot_model.create({'name': 'LOT_03', 'product_id': p3.id})
        wizard.move_lot_ids[1].lot_id = lot_p3

        wizard.do_produce()

        # Check created move in mrp.production
        mrp_order.refresh()
        self.assertEqual(lot_p1,
                         mrp_order.move_created_ids2[0].restrict_lot_id)
        self.assertEqual(lot_p3,
                         mrp_order.move_created_ids2[1].restrict_lot_id)

        # Check stock.quants
        p1_quants = quant_model.search([('product_id', '=', p1.id)])
        self.assertEqual(1, len(p1_quants))
        self.assertEqual(lot_p1, p1_quants.lot_id)
        self.assertEqual(1, p1_quants.qty)

        p3_quants = quant_model.search([('product_id', '=', p3.id)])
        self.assertEqual(1, len(p3_quants))
        self.assertEqual(1, p3_quants.qty)
