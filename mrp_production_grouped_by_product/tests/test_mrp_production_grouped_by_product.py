# Copyright 2018 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests import common


class TestProductionGroupedByProduct(common.SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestProductionGroupedByProduct, cls).setUpClass()
        cls.ProcurementGroup = cls.env['procurement.group']
        cls.MrpProduction = cls.env['mrp.production']
        cls.env.user.company_id.manufacturing_lead = 0
        cls.env.user.tz = False  # Make sure there's no timezone in user
        cls.picking_type = cls.env.ref('mrp.picking_type_manufacturing')
        cls.product1 = cls.env['product.product'].create({
            'name': 'TEST Muffin',
            'route_ids': [(6, 0, [
                cls.env.ref('mrp.route_warehouse0_manufacture').id])],
            'type': 'product',
            'produce_delay': 0,
        })
        cls.product2 = cls.env['product.product'].create({
            'name': 'TEST Paper muffin cup',
            'type': 'product',
        })
        cls.product3 = cls.env['product.product'].create({
            'name': 'TEST Muffin paset',
            'type': 'product',
        })
        cls.bom = cls.env['mrp.bom'].create({
            'product_id': cls.product1.id,
            'product_tmpl_id': cls.product1.product_tmpl_id.id,
            'type': 'normal',
            'bom_line_ids': [(0, 0, {
                'product_id': cls.product2.id,
                'product_qty': 1,
            }), (0, 0, {
                'product_id': cls.product3.id,
                'product_qty': 0.2,
            })]
        })
        cls.stock_picking_type = cls.env.ref('stock.picking_type_out')
        cls.mo = cls.MrpProduction.create({
            'bom_id': cls.bom.id,
            'product_id': cls.product1.id,
            'product_qty': 2,
            'product_uom_id': cls.product1.uom_id.id,
            'date_planned_finished': '2018-06-01 15:00:00',
            'date_planned_start': '2018-06-01 15:00:00',
        })
        cls.warehouse = cls.env['stock.warehouse'].search([
            ('company_id', '=', cls.env.user.company_id.id),
        ], limit=1)
        # Add an MTO move
        cls.move = cls.env['stock.move'].create({
            'name': cls.product1.name,
            'product_id': cls.product1.id,
            'product_uom_qty': 10,
            'product_uom': cls.product1.uom_id.id,
            'location_id': cls.warehouse.lot_stock_id.id,
            'location_dest_id': (
                cls.env.ref('stock.stock_location_customers').id
            ),
            'procure_method': 'make_to_order',
            'warehouse_id': cls.warehouse.id,
            'date': '2018-06-01 18:00:00',
            'date_expected': '2018-06-01 18:00:00',
        })

    def test_mo_by_product(self):
        self.move.with_context(test_group_mo=True)._action_confirm(merge=False)
        self.ProcurementGroup.with_context(test_group_mo=True).run_scheduler()
        mo = self.MrpProduction.search([('product_id', '=', self.product1.id)])
        self.assertEqual(len(mo), 1)
        self.assertEqual(mo.product_qty, 12)
        # Run again the scheduler to see if quantities are altered
        self.ProcurementGroup.with_context(test_group_mo=True).run_scheduler()
        mo = self.MrpProduction.search([('product_id', '=', self.product1.id)])
        self.assertEqual(len(mo), 1)
        self.assertEqual(mo.product_qty, 12)

    def test_mo_other_date(self):
        self.move.write(
            {'date_expected': '2018-06-01 20:01:00',
             'date': '2018-06-01 20:01:00'})
        self.move.with_context(test_group_mo=True)._action_confirm(merge=False)
        self.ProcurementGroup.with_context(test_group_mo=True).run_scheduler()
        mo = self.MrpProduction.search([('product_id', '=', self.product1.id)])
        self.assertEqual(len(mo), 2)

    def test_check_mo_grouping_max_hour(self):
        with self.assertRaises(exceptions.ValidationError):
            self.picking_type.mo_grouping_max_hour = 25
        with self.assertRaises(exceptions.ValidationError):
            self.picking_type.mo_grouping_max_hour = -1

    def test_check_mo_grouping_interval(self):
        with self.assertRaises(exceptions.ValidationError):
            self.picking_type.mo_grouping_interval = -1
