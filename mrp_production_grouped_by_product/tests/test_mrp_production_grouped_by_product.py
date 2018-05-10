# Copyright 2018 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProductionGroupedByProduct(common.SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestProductionGroupedByProduct, cls).setUpClass()
        cls.product1 = cls.env['product.product'].create({
            'name': 'TEST Muffin',
            'route_ids': [(6, 0, [
                cls.env.ref('mrp.route_warehouse0_manufacture').id])],
            'type': 'product',
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
        cls.procurement_rule = cls.env['stock.warehouse.orderpoint'].create({
            'name': 'XXX/00000',
            'product_id': cls.product1.id,
            'product_min_qty': 10,
            'product_max_qty': 100,
        })
        cls.mo = cls.env['mrp.production'].create({
            'bom_id': cls.bom.id,
            'product_id': cls.product1.id,
            'product_qty': 2,
            'product_uom_id': cls.product1.uom_id.id,
        })
        cls.warehouse = cls.env['stock.warehouse'].search([
            ('company_id', '=', cls.env.user.company_id.id),
        ], limit=1)
        cls.ProcurementGroup = cls.env['procurement.group']
        cls.MrpProduction = cls.env['mrp.production']

    def test_mo_by_product(self):
        self.ProcurementGroup.with_context(test_group_mo=True).run_scheduler()
        mo = self.MrpProduction.search([('product_id', '=', self.product1.id)])
        self.assertEqual(len(mo), 1)
        self.assertEqual(mo.product_qty, 100)
        # Add an MTO move
        move = self.env['stock.move'].create({
            'name': self.product1.name,
            'product_id': self.product1.id,
            'product_uom_qty': 10,
            'product_uom': self.product1.uom_id.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'location_dest_id': (
                self.env.ref('stock.stock_location_customers').id
            ),
            'procure_method': 'make_to_order',
            'warehouse_id': self.warehouse.id,
        })
        move.with_context(test_group_mo=True)._action_confirm(merge=False)
        self.ProcurementGroup.with_context(test_group_mo=True).run_scheduler()
        mo = self.MrpProduction.search([('product_id', '=', self.product1.id)])
        self.assertEqual(len(mo), 1)
        self.assertEqual(mo.product_qty, 110)
        # Run again the scheduler to see if quantities are altered
        self.ProcurementGroup.with_context(test_group_mo=True).run_scheduler()
        mo = self.MrpProduction.search([('product_id', '=', self.product1.id)])
        self.assertEqual(len(mo), 1)
        self.assertEqual(mo.product_qty, 110)
