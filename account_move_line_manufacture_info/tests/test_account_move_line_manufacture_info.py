# 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.tests import Form


class TestAccountMoveLineManufactureInfo(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountMoveLineManufactureInfo, cls).setUpClass()

        cls.product_obj = cls.env['product.product']
        cls.account_move_line_obj = cls.env['account.move.line']
        cls.bom_obj = cls.env['mrp.bom']
        cls.bom_line_obj = cls.env['mrp.bom.line']
        cls.location_production = cls.env.ref('stock.location_production')
        cls.production_obj = cls.env['mrp.production']
        cls.produce_wiz = cls.env['mrp.product.produce']
        cls.unbuild_obj = cls.env['mrp.unbuild']

        # Create accounts for WIP
        cls.account_wip = cls.env['account.account'].create({
            'name': 'WIP',
            'code': '999',
            'user_type_id': cls.env.ref(
                'account.data_account_type_current_assets').id
        })

        # Create categories
        cls.categ_physical = cls.env.ref('product.product_category_5')
        cls.categ_physical.write({
            'property_valuation': 'real_time',
        })

        # Assign WIP account to stock location production
        cls.location_production.write({
            'valuation_in_account_id': cls.account_wip.id,
            'valuation_out_account_id': cls.account_wip.id,
        })

        # Create products:
        cls.product_top = cls.product_obj.create({
            'name': 'Final Product',
            'type': 'product',
            'categ_id': cls.categ_physical.id,
        })
        cls.product_sub_1 = cls.product_obj.create({
            'name': 'L01-01',
            'type': 'product',
            'standard_price': 100.0,
            'categ_id': cls.categ_physical.id,
        })
        cls.component_1 = cls.product_obj.create({
            'name': 'RM 01',
            'type': 'product',
            'standard_price': 10.0,
            'categ_id': cls.categ_physical.id,
        })
        cls.component_2 = cls.product_obj.create({
            'name': 'RM 02',
            'type': 'product',
            'standard_price': 15.0,
            'categ_id': cls.categ_physical.id,
        })
        cls.component_3 = cls.product_obj.create({
            'name': 'RM 03',
            'type': 'product',
            'standard_price': 20.0,
            'categ_id': cls.categ_physical.id,
        })

        # Create Bills of Materials:
        cls.bom_top = cls.bom_obj.create({
            'product_tmpl_id': cls.product_top.product_tmpl_id.id,
        })
        cls.line_top_1 = cls.bom_line_obj.create({
            'product_id': cls.product_sub_1.id,
            'bom_id': cls.bom_top.id,
            'product_qty': 2.0,
        })
        cls.line_top_2 = cls.bom_line_obj.create({
            'product_id': cls.component_3.id,
            'bom_id': cls.bom_top.id,
            'product_qty': 3.0,
        })

        cls.bom_sub_1 = cls.bom_obj.create({
            'product_tmpl_id': cls.product_sub_1.product_tmpl_id.id,
        })
        cls.line_sub_1_1 = cls.bom_line_obj.create({
            'product_id': cls.component_1.id,
            'bom_id': cls.bom_sub_1.id,
            'product_qty': 4.0,
        })
        cls.line_sub_1_2 = cls.bom_line_obj.create({
            'product_id': cls.component_2.id,
            'bom_id': cls.bom_sub_1.id,
            'product_qty': 1.0,
        })

    def _produce(self, mo, qty=0.0):
        wiz = Form(self.produce_wiz.with_context({
            'active_id': mo.id,
            'active_ids': [mo.id],
        }))
        wiz.product_qty = qty or mo.product_qty
        produce_wizard = wiz.save()
        produce_wizard.do_produce()
        return True

    def test_01_manufacture_order(self):
        """Create Manufacture Order and check account move lines created"""
        self.product_top.write({
            'standard_price': 445.0,
        })
        mo = self.production_obj.create({
            'name': 'MO-01',
            'product_id': self.product_top.id,
            'product_uom_id': self.product_top.uom_id.id,
            'product_qty': 5.0,
            'bom_id': self.bom_top.id,
        })
        mo.action_assign()
        self._produce(mo, 5.0)
        mo.button_mark_done()
        account_move_lines = self.account_move_line_obj.search([
            ('manufacture_order_id', '=', mo.id)])
        self.assertEqual(len(account_move_lines), 6)

    def test_02_ubuild_order(self):
        """Create Unbuild Order and check account move lines created"""
        self.product_top.write({
            'standard_price': 445.0,
        })
        mo = self.production_obj.create({
            'name': 'MO-01',
            'product_id': self.product_top.id,
            'product_uom_id': self.product_top.uom_id.id,
            'product_qty': 5.0,
            'bom_id': self.bom_top.id,
        })
        mo.action_assign()
        self._produce(mo, 3.0)
        mo.button_mark_done()
        uo = self.unbuild_obj.create({
            'product_id': self.product_top.id,
            'bom_id': self.bom_top.id,
            'product_qty': 1.0,
            'product_uom_id': self.product_top.uom_id.id,
        })
        uo.action_unbuild()
        account_move_lines = self.account_move_line_obj.search([
            ('unbuild_order_id', '=', uo.id)
        ])
        self.assertEqual(len(account_move_lines), 6)
