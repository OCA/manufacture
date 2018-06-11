# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase
from datetime import datetime, timedelta


class TestMultiLevelMRP(SavepointCase):
    def setUp(self):
        super(TestMultiLevelMRP, self).setUp()
        self.wiz_multi_level_mrp_model = self.env['multi.level.mrp']
        self.stock_picking_model = self.env['stock.picking']
        self.mrp_inventory_model = self.env['mrp.inventory']
        self.fp_1 = self.env.ref('multi_level_mrp.product_product_fp_1')
        self.fp_2 = self.env.ref('multi_level_mrp.product_product_fp_2')
        self.sf_1 = self.env.ref('multi_level_mrp.product_product_sf_1')
        self.sf_2 = self.env.ref('multi_level_mrp.product_product_sf_2')
        self.pp_1 = self.env.ref('multi_level_mrp.product_product_pp_1')
        self.pp_2 = self.env.ref('multi_level_mrp.product_product_pp_2')
        self.wh = self.env.ref('stock.warehouse0')
        self.stock_location = self.wh.lot_stock_id
        self.customer_location = self.env.ref(
            'stock.stock_location_customers')
        date_move = datetime.today() + timedelta(days=7)
        self.picking_1 = self.stock_picking_model.create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move pf-1',
                    'product_id': self.fp_1.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': self.fp_1.uom_id.id,
                    'product_uom_qty': 100,
                    'location_id': self.stock_location.id,
                    'location_dest_id': self.customer_location.id
                }),
                (0, 0, {
                    'name': 'Test move fp-2',
                    'product_id': self.fp_2.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': self.fp_2.uom_id.id,
                    'product_uom_qty': 15,
                    'location_id': self.stock_location.id,
                    'location_dest_id': self.customer_location.id
                })]
        })
        self.picking_1.action_confirm()

    def test_mrp_1(self):
        self.wiz_multi_level_mrp_model.create({}).run_multi_level_mrp()
        pp_1_inventory_lines = self.mrp_inventory_model.search(
            [('mrp_product_id.product_id', '=', self.pp_1.id)])
        self.assertEqual(len(pp_1_inventory_lines), 1)
        self.assertEqual(pp_1_inventory_lines.demand_qty, 290)
        self.assertEqual(pp_1_inventory_lines.to_procure, 250)
