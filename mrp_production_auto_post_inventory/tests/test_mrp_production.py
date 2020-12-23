# 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestMrpProductionAutoPost(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestMrpProductionAutoPost, cls).setUpClass()

        cls.product_obj = cls.env['product.product']
        cls.production_obj = cls.env['mrp.production']
        cls.produce_wiz = cls.env['mrp.product.produce']
        cls.company_obj = cls.env['res.company']
        cls.bom_obj = cls.env['mrp.bom']
        cls.bom_line_obj = cls.env['mrp.bom.line']
        cls.stock_move_obj = cls.env['stock.move']

        # Get company
        cls.company_1 = cls.company_obj._company_default_get('mrp.production')

        # Create products:
        cls.product_top = cls.product_obj.create({
            'name': 'Final Product',
            'type': 'product',
        })
        cls.component_1 = cls.product_obj.create({
            'name': 'RM 01',
            'type': 'product',
            'standard_price': 10.0,
        })
        cls.component_2 = cls.product_obj.create({
            'name': 'RM 01',
            'type': 'product',
            'standard_price': 15.0,
        })

        # Create Bills of Materials:
        cls.bom_top = cls.bom_obj.create({
            'product_tmpl_id': cls.product_top.product_tmpl_id.id,
        })
        cls.line_top_1 = cls.bom_line_obj.create({
            'product_id': cls.component_1.id,
            'bom_id': cls.bom_top.id,
            'product_qty': 2.0,
        })
        cls.line_top_2 = cls.bom_line_obj.create({
            'product_id': cls.component_2.id,
            'bom_id': cls.bom_top.id,
            'product_qty': 3.0,
        })

    def _produce(self, mo, qty=0.0):
        wiz = self.produce_wiz.with_context({
            'active_id': mo.id,
            'active_ids': [mo.id],
        }).create({
            'product_qty': qty or mo.product_qty,
        })
        wiz._onchange_product_qty()
        wiz._convert_to_write(wiz._cache)
        wiz.do_produce()
        return True

    def apply_cron(self):
        self.env.ref('mrp_production_auto_post_inventory.'
                     'ir_cron_mrp_production_post_inventory').method_direct_trigger()

    def test_01_manufacture_order_no_auto_post(self):
        """Create Manufacture Order with auto post inventory False"""
        self.company_1.mrp_production_auto_post_inventory = False
        mo = self.production_obj.create({
            'name': 'MO-01',
            'product_id': self.product_top.id,
            'product_uom_id': self.product_top.uom_id.id,
            'product_qty': 5.0,
            'bom_id': self.bom_top.id,
            'company_id': self.company_1.id,
        })
        mo.action_assign()
        self._produce(mo, 1.0)
        raw_moves = self.stock_move_obj.search([
            ('raw_material_production_id', '=', mo.id),
            ('state', '=', 'done')]
        )
        finished_moves = self.stock_move_obj.search([
            ('production_id', '=', mo.id),
            ('state', '=', 'done')]
        )
        self.assertEqual(len(raw_moves), 0)
        self.assertEqual(len(finished_moves), 0)

    def test_02_manufacture_order_auto_post(self):
        """Create Manufacture Order with auto post inventory True"""
        self.company_1.mrp_production_auto_post_inventory = True
        mo = self.production_obj.create({
            'name': 'MO-01',
            'product_id': self.product_top.id,
            'product_uom_id': self.product_top.uom_id.id,
            'product_qty': 5.0,
            'bom_id': self.bom_top.id,
            'company_id': self.company_1.id,
        })
        mo.action_assign()
        self._produce(mo, 1.0)
        raw_moves = self.stock_move_obj.search([
            ('raw_material_production_id', '=', mo.id),
            ('state', '=', 'done')]
        )
        finished_moves = self.stock_move_obj.search([
            ('production_id', '=', mo.id),
            ('state', '=', 'done')]
        )
        self.assertEqual(len(raw_moves), 2)
        self.assertEqual(len(finished_moves), 1)

    def test_03_manufacture_order_auto_post_cron(self):
        """Create Manufacture Order with auto post inventory True and use Cron Job"""
        self.company_1.mrp_production_auto_post_inventory = True
        self.company_1.mrp_production_auto_post_inventory_cron = True
        mo = self.production_obj.create({
            'name': 'MO-01',
            'product_id': self.product_top.id,
            'product_uom_id': self.product_top.uom_id.id,
            'product_qty': 5.0,
            'bom_id': self.bom_top.id,
            'company_id': self.company_1.id,
        })
        mo.action_assign()
        self._produce(mo, 1.0)
        self.assertTrue(mo.to_post_inventory_cron)  # To post by cron job
        # Waiting for job
        raw_moves = self.stock_move_obj.search([
            ('raw_material_production_id', '=', mo.id),
            ('state', '=', 'done')]
        )
        finished_moves = self.stock_move_obj.search([
            ('production_id', '=', mo.id),
            ('state', '=', 'done')]
        )
        self.assertEqual(len(raw_moves), 0)
        self.assertEqual(len(finished_moves), 0)
        # Run the job
        self.apply_cron()
        self.assertFalse(mo.to_post_inventory_cron)  # Posted by cron job
        raw_moves = self.stock_move_obj.search([
            ('raw_material_production_id', '=', mo.id),
            ('state', '=', 'done')]
        )
        finished_moves = self.stock_move_obj.search([
            ('production_id', '=', mo.id),
            ('state', '=', 'done')]
        )
        self.assertEqual(len(raw_moves), 2)
        self.assertEqual(len(finished_moves), 1)
