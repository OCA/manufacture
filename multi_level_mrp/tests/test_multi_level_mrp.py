# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.tests.common import SavepointCase
from odoo import fields


class TestMultiLevelMRP(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestMultiLevelMRP, cls).setUpClass()
        cls.wiz_multi_level_mrp_model = cls.env['multi.level.mrp']
        cls.stock_picking_model = cls.env['stock.picking']
        cls.mrp_inventory_model = cls.env['mrp.inventory']
        cls.fp_1 = cls.env.ref('multi_level_mrp.product_product_fp_1')
        cls.fp_2 = cls.env.ref('multi_level_mrp.product_product_fp_2')
        cls.sf_1 = cls.env.ref('multi_level_mrp.product_product_sf_1')
        cls.sf_2 = cls.env.ref('multi_level_mrp.product_product_sf_2')
        cls.pp_1 = cls.env.ref('multi_level_mrp.product_product_pp_1')
        cls.pp_2 = cls.env.ref('multi_level_mrp.product_product_pp_2')
        cls.wh = cls.env.ref('stock.warehouse0')
        cls.stock_location = cls.wh.lot_stock_id
        cls.customer_location = cls.env.ref(
            'stock.stock_location_customers')
        date_move = datetime.today() + timedelta(days=7)
        cls.picking_1 = cls.stock_picking_model.create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.customer_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move pf-1',
                    'product_id': cls.fp_1.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.fp_1.uom_id.id,
                    'product_uom_qty': 100,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                }),
                (0, 0, {
                    'name': 'Test move fp-2',
                    'product_id': cls.fp_2.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.fp_2.uom_id.id,
                    'product_uom_qty': 15,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                })]
        })
        cls.picking_1.action_confirm()
        cls.wiz_multi_level_mrp_model.create({}).run_multi_level_mrp()

    def test_01_mrp_levels(self):
        """Tests computation of MRP levels."""
        self.assertEqual(self.fp_1.llc, 0)
        self.assertEqual(self.fp_2.llc, 0)
        self.assertEqual(self.sf_1.llc, 1)
        self.assertEqual(self.sf_2.llc, 1)
        self.assertEqual(self.pp_1.llc, 2)
        self.assertEqual(self.pp_2.llc, 2)

    def test_02_multi_level_mrp(self):
        """Tests MRP inventories created."""
        # FP-1
        fp_1_inventory_lines = self.mrp_inventory_model.search(
            [('mrp_product_id.product_id', '=', self.fp_1.id)])
        self.assertEqual(len(fp_1_inventory_lines), 1)
        date_7 = fields.Date.to_string(datetime.today() + timedelta(days=7))
        self.assertEqual(fp_1_inventory_lines.date, date_7)
        self.assertEqual(fp_1_inventory_lines.demand_qty, 100.0)
        self.assertEqual(fp_1_inventory_lines.to_procure, 100.0)
        # FP-2
        fp_2_inventory_lines = self.mrp_inventory_model.search(
            [('mrp_product_id.product_id', '=', self.fp_2.id)])
        self.assertEqual(len(fp_2_inventory_lines), 1)
        self.assertEqual(fp_2_inventory_lines.date, date_7)
        self.assertEqual(fp_2_inventory_lines.demand_qty, 15.0)
        self.assertEqual(fp_2_inventory_lines.to_procure, 15.0)

        # SF-1
        sf_1_inventory_lines = self.mrp_inventory_model.search(
            [('mrp_product_id.product_id', '=', self.sf_1.id)])
        self.assertEqual(len(sf_1_inventory_lines), 1)
        date_6 = fields.Date.to_string(datetime.today() + timedelta(days=6))
        self.assertEqual(sf_1_inventory_lines.date, date_6)
        self.assertEqual(sf_1_inventory_lines.demand_qty, 30.0)
        self.assertEqual(sf_1_inventory_lines.to_procure, 30.0)
        # SF-2
        sf_2_inventory_lines = self.mrp_inventory_model.search(
            [('mrp_product_id.product_id', '=', self.sf_2.id)])
        self.assertEqual(len(sf_2_inventory_lines), 1)
        self.assertEqual(sf_2_inventory_lines.date, date_6)
        self.assertEqual(sf_2_inventory_lines.demand_qty, 45.0)
        self.assertEqual(sf_2_inventory_lines.to_procure, 30.0)

        # PP-1
        pp_1_inventory_lines = self.mrp_inventory_model.search(
            [('mrp_product_id.product_id', '=', self.pp_1.id)])
        self.assertEqual(len(pp_1_inventory_lines), 1)
        date_5 = fields.Date.to_string(datetime.today() + timedelta(days=5))
        self.assertEqual(pp_1_inventory_lines.date, date_5)
        self.assertEqual(pp_1_inventory_lines.demand_qty, 290.0)
        self.assertEqual(pp_1_inventory_lines.to_procure, 280.0)
        # PP-2
        pp_2_line_1 = self.mrp_inventory_model.search([
            ('mrp_product_id.product_id', '=', self.pp_2.id),
            ('date', '=', date_5)])
        self.assertEqual(len(pp_2_line_1), 1)
        self.assertEqual(pp_2_line_1.demand_qty, 360.0)
        self.assertEqual(pp_2_line_1.to_procure, 360.0)
        date_3 = fields.Date.to_string(datetime.today() + timedelta(days=3))
        pp_2_line_2 = self.mrp_inventory_model.search([
            ('mrp_product_id.product_id', '=', self.pp_2.id),
            ('date', '=', date_3)])
        self.assertEqual(len(pp_2_line_2), 1)
        self.assertEqual(pp_2_line_2.demand_qty, 90.0)
        self.assertEqual(pp_2_line_2.to_procure, 70.0)

    # TODO: test procure wizard: dates...
