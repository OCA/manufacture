# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.tests import Form


class TestProductionGroupLine(common.TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestProductionGroupLine, self).setUp(*args, **kwargs)
        self.production_model = self.env['mrp.production']
        self.procurement_model = self.env['procurement.group']
        self.bom_model = self.env['mrp.bom']
        self.stock_location_stock = self.env.ref('stock.stock_location_stock')
        self.manufacture_route = self.env.ref(
            'mrp.route_warehouse0_manufacture')
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.top_product = self.env.ref(
            'mrp_production_line_group.product_product_manufacture_1')
        self.subproduct1 = self.env.ref(
            'mrp_production_line_group.product_product_manufacture_1_1')
        self.subproduct2 = self.env.ref(
            'mrp_production_line_group.product_product_manufacture_1_2')
        self.subproduct_1_1 = self.env.ref(
            'mrp_production_line_group.product_product_manufacture_1_1_1')
        self.subproduct_2_1 = self.env.ref(
            'mrp_production_line_group.product_product_manufacture_1_2_1')
        self.main_bom = self.env.ref('mrp_production_line_group.mrp_bom_manuf_1')

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

    def test_mo_by_product(self):
        self._update_product_qty(self.subproduct_1_1, self.stock_location_stock, 16*3)
        self.production = self.production_model.create(self._get_production_vals())
        self.production.action_assign()

        self.assertEqual(self.production.availability, 'partially_available')
        self.assertEquals(self.subproduct_1_1.virtual_available, 16*2)

        wizard_obj = self.env['production.group.line.wizard']
        wizard_vals = wizard_obj.with_context(
            active_id=self.production.id,
            active_model='mrp.production').default_get(
                ['mo_id']
            )
        wizard = wizard_obj.create(wizard_vals)
        wizard.action_done()
        self.assertEqual(len(self.production), 1)
        self.assertEqual(len(self.production.move_raw_ids), 2)
        # 5*2=10 in sub1, 2*3=6 in sub2
        self.assertEqual(self.production.move_raw_ids.filtered(
            lambda x: x.product_id == self.subproduct_1_1
        ).product_uom_qty, 16)
        self._update_product_qty(self.subproduct_2_1, self.stock_location_stock, 8*3)

        # check change.production.qty is callable, but it split lines again
        change_qty_wizard = self.env['change.production.qty'].create({
            'mo_id': self.production.id,
            'product_qty': 3.0,
        })
        change_qty_wizard.change_prod_qty()
        wizard_obj = self.env['production.group.line.wizard']
        wizard_vals = wizard_obj.with_context(
            active_id=self.production.id,
            active_model='mrp.production').default_get(
            ['mo_id']
        )
        wizard = wizard_obj.create(wizard_vals)
        wizard.action_done()

        self.production.action_assign()
        self.assertEquals(self.subproduct_1_1.virtual_available, 0)
        self.assertEquals(self.subproduct_2_1.virtual_available, 0)
        self.assertEqual(self.production.availability, 'assigned')
        produce_form = Form(self.env['mrp.product.produce'].with_context(
            active_id=self.production.id,
            active_ids=[self.production.id],
        ))
        produce_form.product_qty = 3.0
        wizard = produce_form.save()
        wizard.do_produce()
        self.assertEqual(len(self.production), 1)
        self.assertEqual(self.production.move_raw_ids.filtered(
            lambda x: x.product_id == self.subproduct_1_1
        ).unit_factor, 16)
        self.assertEqual(
            self.production.move_raw_ids.mapped('product_uom_qty'), [16 * 3, 8 * 3])
        self.assertEqual(
            self.production.move_raw_ids.mapped('quantity_done'), [16 * 3, 8 * 3])
        self.production.button_mark_done()
        self.assertEqual(self.production.availability, 'assigned')
        self.assertEquals(self.top_product.qty_available, 3)
