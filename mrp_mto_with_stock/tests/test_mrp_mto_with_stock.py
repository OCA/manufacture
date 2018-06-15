# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMrpMtoWithStock(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestMrpMtoWithStock, self).setUp(*args, **kwargs)
        self.production_model = self.env['mrp.production']
        self.procurement_model = self.env['procurement.group']
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
        self.subproduct1_bom_id = self.ref(
            'mrp_mto_with_stock.mrp_bom_manuf_1_1')

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

    def _setup_wizard(self, mo_id):
        MrpProductProduce = self.env['mrp.product.produce']
        default_fields = ['lot_id', 'product_id', 'product_uom_id',
                          'product_tracking', 'consume_line_ids',
                          'production_id', 'product_qty', 'serial']
        wizard_vals = MrpProductProduce.with_context(
            active_id=mo_id).default_get(default_fields)
        return MrpProductProduce.create(wizard_vals)

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
        production_sub1 = self.production_model.search(
            [('origin', 'ilike', self.production.name)])
        self.assertEqual(production_sub1.state, 'confirmed')
        self.assertEquals(len(production_sub1), 1)
        self.assertEqual(production_sub1.product_qty, 3)
        self._update_product_qty(self.subproduct1, self.stock_location_stock,
                                 7)

        # Create second MO and check it does not create procurement
        self.production2 = self.production_model.create(
            self._get_production_vals())
        self.production2.action_assign()
        p = self.production_model.search(
            [('origin', 'ilike', self.production2.name)])
        self.assertEquals(len(p), 0)
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
        mo = self.production_model.search(
            [('origin', 'ilike', self.production.name)])
        self.assertEqual(mo.product_qty, 3)

        mo.action_assign()
        self.assertEqual(mo.availability, 'assigned')

        wizard = self._setup_wizard(mo.id)
        wizard.do_produce()

        self.assertEqual(len(mo), 1)
        mo.button_mark_done()
        self.assertEqual(mo.availability, 'assigned')
        self.assertEquals(self.subproduct1.qty_available, 5)

        self.production.action_assign()
        self.assertEqual(self.production.state, 'confirmed')

        # wizard = wizard_obj.create(wizard_vals)
        wizard = self._setup_wizard(self.production.id)
        wizard.do_produce()

        self.assertTrue(self.production.check_to_done)
        self.production.button_mark_done()
        self.assertEqual(self.production.state, 'done')
        self.assertEquals(self.subproduct2.qty_available, 2)

    def test_consumed_material_split(self):
        """Test MO when not all qty is available and we need split.

        We use default mode (without forecast quantity) to have a link
        with MO.
        """
        # Set location on subproduct, so it would trigger MTO/MTS
        # functionality. Also add vendor, otherwise, UserError would
        # be raised when it tries to create PO for missing quantity.
        self.subproduct_1_1.write({
            'mrp_mts_mto_location_ids': [
                (6, 0, self.stock_location_stock.ids)],
            'seller_ids': [
                (
                    0, 0,
                    {'name': self.ref('base.res_partner_1'), 'price': 10.0}
                )
            ]
        })
        # Sanity assertion.
        self.assertEqual(self.subproduct_1_1.qty_available, 0)
        # Set init quantity for sub-sub product that is used in this MO.
        self._update_product_qty(
            self.subproduct_1_1, self.stock_location_stock, 5)
        mo_vals = {
            'product_id': self.subproduct1.id,
            'product_qty': 7,
            'product_uom_id': self.uom_unit.id,
            'bom_id': self.subproduct1_bom_id,
        }
        mo = self.production_model.create(mo_vals)
        orig_move = mo.move_raw_ids[0]  # Expect 1 stock.move rec here.
        # unit_factor 14 / 7 = 2, because for every product produced we
        # need 2 units of materials.
        self.assertEqual(orig_move.unit_factor, 2)
        mo.action_assign()
        self.assertEqual(mo.availability, 'partially_available')
        # We now need to have second move added after running
        # `action_assign`.
        new_move = mo.move_raw_ids - orig_move
        # Check `unit_factor`. It had to be updated after split.
        # Because original move now expects only 5 units used, thus:
        # 5 / 7 ~= 0.71429.
        # We use full expression here, because we expect not rounded
        # value.
        self.assertEqual(orig_move.unit_factor, 5/7)
        # We also check new_move, because it is now responsible for the
        # rest of materials. Thus:
        # (14 - 5) / 7 ~= 1.28571.
        self.assertEqual(new_move.unit_factor, 9/7)
        # Update material product quantity to meed MO requirements, so
        # we could finish MO.
        self._update_product_qty(
            self.subproduct_1_1, self.stock_location_stock, 14)
        # Reserve required materials again.
        mo.action_assign()
        # Recheck that `unit_factor` did not change.
        self.assertEqual(orig_move.unit_factor, 5/7)
        self.assertEqual(new_move.unit_factor, 9/7)
        # Finish MO.
        wizard = self._setup_wizard(mo.id)
        wizard.do_produce()
        mo.button_mark_done()
        self.assertEqual(mo.state, 'done')
        self.assertEqual(self.subproduct1.qty_available, 7)
        # Check that have only two moves in raw moves and that no
        # extra moves appeared after finishing MO.
        self.assertEqual(len(mo.move_raw_ids), 2)
        # We used all materials we had, so expected quantity should be
        # 0 now.
        self.assertEqual(self.subproduct_1_1.qty_available, 0)
