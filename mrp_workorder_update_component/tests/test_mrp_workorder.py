# Copyright 2023 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import Form


@tagged("-at_install", "post_install")
class TestMrpWorkorderUpdateComponent(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMrpWorkorderUpdateComponent, cls).setUpClass()

        cls.categ_obj = cls.env["product.category"]
        cls.product_obj = cls.env["product.product"]
        cls.bom_obj = cls.env["mrp.bom"]
        cls.bom_line_obj = cls.env["mrp.bom.line"]
        cls.production_obj = cls.env["mrp.production"]
        cls.produce_wiz = cls.env["mrp.product.produce"]
        cls.wc_obj = cls.env["mrp.workcenter"]
        cls.routing_obj = cls.env["mrp.routing"]
        cls.sm_obj = cls.env["stock.move"]
        cls.picking_obj = cls.env["stock.picking"]
        cls.lot_obj = cls.env["stock.production.lot"]
        cls.partner_obj = cls.env["res.partner"]
        cls.company = cls.env.ref("base.main_company")
        cls.src_location = cls.env.ref("stock.stock_location_stock")
        manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        mto_route = cls.env.ref("stock.route_warehouse0_mto")

        # Create Partner:
        cls.partner = cls.partner_obj.create(
            {"name": "Test Customer", "email": "example@custemer-test.com"}
        )

        # Create products and lots:
        cls.product_1 = cls.product_obj.create(
            {
                "name": "TEST 01",
                "type": "product",
                "tracking": "lot",
                "route_ids": [(6, 0, [mto_route.id, manufacture_route.id])],
            }
        )
        cls.product_1_lot = cls.lot_obj.create(
            {
                "name": "LotABC",
                "product_id": cls.product_1.id,
                "company_id": cls.company.id,
            }
        )
        cls.component_1 = cls.product_obj.create(
            {
                "name": "RM 01",
                "type": "product",
                "standard_price": 100.0,
                "tracking": "lot",
            }
        )
        cls.component_1_lot = cls.lot_obj.create(
            {
                "name": "Lot1",
                "product_id": cls.component_1.id,
                "company_id": cls.company.id,
            }
        )
        cls.component_1_lot_2 = cls.lot_obj.create(
            {
                "name": "Lot2",
                "product_id": cls.component_1.id,
                "company_id": cls.company.id,
            }
        )

        # Create Bills of Materials:
        test_wc = cls.wc_obj.create({"name": "Test WC", "company_id": cls.company.id})
        routing = cls.routing_obj.create(
            {
                "name": "Test Routing",
                "company_id": cls.company.id,
                "operation_ids": [
                    (0, 0, {"name": "Single operation", "workcenter_id": test_wc.id})
                ],
            }
        )
        cls.bom_1 = cls.bom_obj.create(
            {
                "product_tmpl_id": cls.product_1.product_tmpl_id.id,
                "routing_id": routing.id,
                "company_id": cls.company.id,
            }
        )
        cls.bom_line_obj.create(
            {
                "product_id": cls.component_1.id,
                "bom_id": cls.bom_1.id,
                "product_qty": 5.0,
            }
        )

    def test_01_change_lot(self):
        self.env["stock.quant"]._update_available_quantity(
            self.component_1, self.src_location, 5, lot_id=self.component_1_lot
        )
        self.env["stock.quant"]._update_available_quantity(
            self.component_1, self.src_location, 2, lot_id=self.component_1_lot_2
        )
        mo = self.production_obj.create(
            {
                "product_id": self.product_1.id,
                "bom_id": self.bom_1.id,
                "location_src_id": self.src_location.id,
                "location_dest_id": self.src_location.id,
                "product_qty": 1,
                "product_uom_id": self.product_1.uom_id.id,
            }
        )
        mo._onchange_move_raw()
        mo.action_confirm()
        mo.action_assign()
        mo.button_plan()
        workorder = mo.workorder_ids
        self.assertTrue(workorder)
        self.assertEqual(len(mo.move_raw_ids.move_line_ids), 1)
        self.assertEqual(len(workorder.raw_workorder_line_ids), 1)
        old_ml = mo.move_raw_ids.move_line_ids
        old_wol = workorder.raw_workorder_line_ids
        self.assertEqual(old_ml.product_uom_qty, 5)
        self.assertEqual(old_ml.lot_id, self.component_1_lot)
        self.assertEqual(old_wol.qty_to_consume, 5)
        self.assertEqual(old_wol.qty_reserved, 5)
        self.assertEqual(old_wol.lot_id, self.component_1_lot)
        wiz_dict = workorder.raw_workorder_line_ids.action_new_line_wizard()
        mrp_wo_nl = Form(
            self.env["mrp.workorder.new.line"].with_context(wiz_dict["context"])
        )
        mrp_wo_nl.lot_id = self.component_1_lot_2
        mrp_wo_nl.product_qty = 6
        with self.assertRaises(
            ValidationError,
            msg="The quantity must be lower than the original line quantity: 5.",
        ):
            mrp_wo_nl.save()
        mrp_wo_nl.product_qty = 3
        mrp_wo = mrp_wo_nl.save()
        with self.assertRaises(
            ValidationError,
            msg="The quantity must be lower or equal than the available quantity: 2.",
        ):
            mrp_wo.action_validate()
        mrp_wo_nl.product_qty = 2
        mrp_wo = mrp_wo_nl.save()
        mrp_wo.action_validate()
        self.assertEqual(len(mo.move_raw_ids.move_line_ids), 2)
        self.assertEqual(len(workorder.raw_workorder_line_ids), 2)
        new_ml = mo.move_raw_ids.move_line_ids.filtered(lambda ml: ml.id != old_ml.id)
        new_wol = workorder.raw_workorder_line_ids.filtered(
            lambda wol: wol.id != old_wol.id
        )
        self.assertEqual(old_ml.product_uom_qty, 3)
        self.assertEqual(old_ml.lot_id, self.component_1_lot)
        self.assertEqual(old_wol.qty_to_consume, 3)
        self.assertEqual(old_wol.qty_reserved, 3)
        self.assertEqual(old_wol.lot_id, self.component_1_lot)
        self.assertEqual(new_ml.product_uom_qty, 2)
        self.assertEqual(new_ml.lot_id, self.component_1_lot_2)
        self.assertEqual(new_wol.qty_to_consume, 2)
        self.assertEqual(new_wol.qty_reserved, 2)
        self.assertEqual(new_wol.lot_id, self.component_1_lot_2)
