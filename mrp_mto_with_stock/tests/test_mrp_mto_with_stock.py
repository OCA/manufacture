# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMrpMtoWithStock(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestMrpMtoWithStock, self).setUp(*args, **kwargs)
        self.production_model = self.env['mrp.production']
        self.bom_model = self.env['mrp.bom']
        self.stock_location_stock = self.env.ref('stock.stock_location_stock')
        self.manufacture_route = self.env.ref(
            'mrp.route_warehouse0_manufacture')
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.warehouse = self.env.ref('stock.warehouse0')

        self.top_product = self.env.ref(
            'mrp_mto_with_stock.product_product_manufacture_1')
        self.subproduct1 = self.env.ref(
            'mrp_mto_with_stock.product_product_manufacture_1_1')
        self.subproduct2 = self.env.ref(
            'mrp_mto_with_stock.product_product_manufacture_1_2')
        self.subproduct_1_1 = self.env.ref(
            'mrp_mto_with_stock.product_product_manufacture_1_1_1')

        self.main_bom = self.env.ref(
            'mrp_mto_with_stock.mrp_bom_manuf_1')

    def _get_production_vals(self):
        return {
            'product_id': self.top_product.id,
            'product_qty': 1,
            'product_uom_id': self.uom_unit.id,
            'bom_id': self.main_bom.id,
        }

    def _update_product_qty(self, product, location, quantity):
        """Update Product quantity."""
        product_qty = self.env['stock.change.product.qty'].create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        product_qty.change_product_qty()
        return product_qty

    def test_manufacture_with_forecast_stock(self):
        """
            Test Manufacture mto with stock based on forecast quantity
            and no link between sub assemblies MO's and Main MO raw material
        """

        self.warehouse.mrp_mto_mts_forecast_qty = True

        self._update_product_qty(self.subproduct1, self.stock_location_stock,
                                 2)
        self._update_product_qty(self.subproduct2, self.stock_location_stock,
                                 4)

        self.production = self.production_model.create(
            self._get_production_vals())

        # Create MO and check it create sub assemblie MO.
        self.production.action_assign()

        self.assertEqual(self.production.availability, 'partially_available')

        self.assertEquals(self.subproduct1.virtual_available, 0)

        procurement_subproduct1 = self.env['procurement.order'].search(
            [('product_id', '=', self.subproduct1.id),
             ('group_id', '=', self.production.procurement_group_id.id)])

        self.assertEquals(len(procurement_subproduct1), 1)
        self.assertEquals(procurement_subproduct1.product_qty, 3)

        production_sub1 = procurement_subproduct1.production_id
        self.assertEqual(production_sub1.state, 'confirmed')
        self.assertEqual(production_sub1.product_qty, 3)

        self._update_product_qty(self.subproduct1, self.stock_location_stock,
                                 7)

        # Create second MO and check it does not create procurement
        self.production2 = self.production_model.create(
            self._get_production_vals())
        self.production2.action_assign()
        procurement_subproduct1_2 = self.env['procurement.order'].search(
            [('product_id', '=', self.subproduct1.id),
             ('group_id', '=', self.production2.procurement_group_id.id)])
        self.assertEquals(len(procurement_subproduct1_2), 0)
        self.assertEquals(self.production2.availability, 'assigned')
        self.production2.do_unreserve()

        self.assertEquals(self.subproduct1.virtual_available, 0)

        self.production.action_assign()
        # We check if first MO is able to assign it self even if it has
        # previously generate procurements, it would not be the case in the
        # other mode (without mrp_mto_mts_reservable_stock on warehouse)
        self.assertEquals(self.production.availability, 'assigned')

        self.assertEquals(self.subproduct1.virtual_available, 0)

    def test_manufacture_with_reservable_stock(self):
        """
            Test Manufacture mto with stock based on reservable stock
            and there is a link between sub assemblies MO's and Main MO raw
            materi  al
        """

        self._update_product_qty(self.subproduct1, self.stock_location_stock,
                                 2)
        self._update_product_qty(self.subproduct2, self.stock_location_stock,
                                 4)

        self.production = self.production_model.create(
            self._get_production_vals())

        self._update_product_qty(self.subproduct_1_1,
                                 self.stock_location_stock, 50)

        # Create MO and check it create sub assemblie MO.
        self.production.action_assign()
        self.assertEqual(self.production.state, 'confirmed')

        procurement_sub1 = self.env['procurement.order'].search(
            [('product_id', '=', self.subproduct1.id),
             ('move_dest_id', 'in', self.production.move_raw_ids.ids)])
        self.assertEquals(len(procurement_sub1), 1)

        procurement_sub2 = self.env['procurement.order'].search(
            [('product_id', '=', self.subproduct2.id),
             ('move_dest_id', 'in', self.production.move_raw_ids.ids)])
        self.assertEquals(len(procurement_sub2), 0)

        production_sub1 = procurement_sub1.production_id
        self.assertEqual(production_sub1.product_qty, 3)
        production_sub1.action_assign()
        self.assertEqual(production_sub1.availability, 'assigned')

        wizard_obj = self.env['mrp.product.produce']
        default_fields = ['lot_id', 'product_id', 'product_uom_id',
                          'product_tracking', 'consume_line_ids',
                          'production_id', 'product_qty', 'serial']
        wizard_vals = wizard_obj.with_context(active_id=production_sub1.id).\
            default_get(default_fields)

        wizard = wizard_obj.create(wizard_vals)
        wizard.do_produce()
        self.assertTrue(production_sub1.check_to_done)
        self.assertEquals(self.subproduct1.qty_available, 2)
        production_sub1.button_mark_done()
        self.assertEquals(self.subproduct1.qty_available, 5)
        self.assertEqual(self.production.availability, 'assigned')
