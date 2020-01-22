# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
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
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.warehouse.write({
            'manufacture_to_resupply': True,
            'manufacture_steps': 'pbm',
            'mto_mts_management': True,
        })

        self.top_product = self.env.ref(
            'mrp_mto_with_stock_lite.product_product_manufacture_1')
        self.subproduct1 = self.env.ref(
            'mrp_mto_with_stock_lite.product_product_manufacture_1_1')
        self.subproduct2 = self.env.ref(
            'mrp_mto_with_stock_lite.product_product_manufacture_1_2')
        self.subproduct_1_1 = self.env.ref(
            'mrp_mto_with_stock_lite.product_product_manufacture_1_1_1')

        self.main_bom = self.env.ref(
            'mrp_mto_with_stock_lite.mrp_bom_manuf_1')

    def test_mts_mto_rule_constrains(self):
        with self.assertRaises(ValidationError):
            self.warehouse.write({
                'mto_mts_management': True,
                'manufacture_to_resupply': True,
                'manufacture_steps': 'mrp_one_step',
            })

    def test_rename_warehouse(self):
        rule = self.warehouse.pbm_mts_mto_rule_id
        new_warehouse_name = 'NewName'
        new_rule_name = rule.name.replace(
            self.warehouse.name, new_warehouse_name, 1)
        self.warehouse.name = new_warehouse_name
        self.assertEqual(new_rule_name, rule.name)

    def _get_production_vals(self):
        manu_type = self.warehouse.manu_type_id
        return {
            'product_id': self.top_product.id,
            'product_qty': 1,
            'product_uom_id': self.uom_unit.id,
            'bom_id': self.main_bom.id,
            # not correct location if manufacture_step != 'mrp_one_step'
            'picking_type_id': manu_type.id,
            'location_src_id': manu_type.default_location_src_id.id,
            'location_dest_id': manu_type.default_location_dest_id.id,
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

    def _get_pre_production_picking(self, production):
        return production.move_raw_ids.mapped("move_orig_ids.picking_id")

    def _move_to_pre_production(self, production):
        pre_production = self._get_pre_production_picking(production)
        pre_production.action_assign()
        for ml in pre_production.move_line_ids:
            ml.qty_done = ml.product_uom_qty
        wiz = self.env['stock.backorder.confirmation'].create({
            'pick_ids': [(4, pre_production.id)],
        })
        wiz.process()

    def _produce_mo(self, production):
        wizard_obj = self.env['mrp.product.produce']
        default_fields = ['lot_id', 'product_id', 'product_uom_id',
                          'product_tracking', 'consume_line_ids',
                          'production_id', 'product_qty', 'serial']
        wizard_vals = wizard_obj.with_context(active_id=production.id). \
            default_get(default_fields)
        wizard = wizard_obj.create(wizard_vals)
        wizard._onchange_product_qty()
        wizard.do_produce()

    def test_manufacture_with_forecast_stock(self):
        """
            Test Manufacture mto with stock based on forecast quantity
            and no link between sub assemblies MO's and Main MO raw material
        """

        self._update_product_qty(self.subproduct1, self.stock_location_stock,
                                 2)
        self._update_product_qty(self.subproduct2, self.stock_location_stock,
                                 4)

        # Create MO and check it create sub assemblies MO.
        self.production = self.production_model.create(
            self._get_production_vals())
        self.assertEqual(self.production.availability, 'waiting')
        pre_production_picking = self._get_pre_production_picking(
            self.production)
        pre_production_picking.action_assign()
        self.assertEqual(pre_production_picking.state, 'assigned')
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
        pre_production_picking = self._get_pre_production_picking(
            self.production2)
        pre_production_picking.action_assign()
        p = self.production_model.search(
            [('origin', 'ilike', self.production2.name)])
        self.assertEquals(len(p), 0)
        self.assertEquals(pre_production_picking.state, 'assigned')
        pre_production_picking.do_unreserve()
        self.assertEquals(self.subproduct1.virtual_available, 0)

        pre_production_picking = self._get_pre_production_picking(
            self.production)
        # We check if first MO is able to assign it self even if it has
        # previously generate procurements, it would not be the case in the
        # other mode (without mrp_mto_mts_reservable_stock on warehouse)
        self.assertEquals(pre_production_picking.state, 'assigned')

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
        self._update_product_qty(self.subproduct_1_1,
                                 self.stock_location_stock, 50)

        self.production = self.production_model.create(
            self._get_production_vals())
        self.assertEqual(
            len(self.production.move_raw_ids.mapped("move_orig_ids")), 3)

        # Create MO and check it create sub assemblies MO.
        mo = self.production_model.search(
            [('origin', 'ilike', self.production.name)])
        self.assertEqual(mo.product_qty, 3)

        self._move_to_pre_production(mo)
        self.assertEqual(mo.availability, 'assigned')
        self._produce_mo(mo)
        self.assertEqual(len(mo), 1)
        mo.button_mark_done()
        self.assertEqual(mo.availability, 'assigned')
        self.assertEquals(self.subproduct1.qty_available, 5)

        self.production.action_assign()
        self.assertEqual(self.production.state, 'confirmed')
        self._move_to_pre_production(self.production)

        self._produce_mo(self.production)
        # Check that not extra moves were generated and qty's are ok:
        self.assertEqual(
            len(self.production.move_raw_ids.mapped("move_orig_ids")), 3)
        for move in self.production.move_raw_ids.mapped("move_orig_ids"):
            if move.product_id == self.subproduct1 and \
                    move.procure_method == 'make_to_order':
                qty = 3.0
            else:
                qty = 2.0
            self.assertEqual(move.quantity_done, qty)

        self.assertTrue(self.production.check_to_done)
        self.production.button_mark_done()
        self.assertEqual(self.production.state, 'done')
        self.assertEquals(self.subproduct2.qty_available, 2)
