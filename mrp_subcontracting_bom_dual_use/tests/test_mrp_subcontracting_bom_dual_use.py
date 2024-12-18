# Copyright 2022-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, new_test_user
from odoo.tests.common import users

from odoo.addons.base.tests.common import BaseCommon


class TestMrpSubcontractingBomDualUse(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
                "route_ids": [(6, 0, [cls.manufacture_route.id])],
            }
        )
        cls.component_a = cls.env["product.product"].create({"name": "Test Comp A"})
        cls.workcenter = cls.env["mrp.workcenter"].create({"name": "Test workcenter"})
        cls.mrp_production_model = cls.env["mrp.production"]
        new_test_user(
            cls.env,
            login="test_mrp_routings_user",
            groups="mrp.group_mrp_routings,mrp.group_mrp_manager",
        )

    @classmethod
    def _create_bom(cls, bom_type):
        mrp_bom_form = Form(cls.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = cls.product.product_tmpl_id
        mrp_bom_form.type = bom_type
        if bom_type == "subcontract":
            mrp_bom_form.subcontractor_ids.add(cls.partner)
            mrp_bom_form.allow_in_regular_production = True
        mrp_bom_form.product_tmpl_id = cls.product.product_tmpl_id
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = cls.component_a
            line_form.product_qty = 1
        return mrp_bom_form.save()

    def test_mrp_production_misc_bom_normal(self):
        """We create a BOM of normal type. We create a production order and assign
        the product to check that the BOM is assigned correctly."""
        bom = self._create_bom("normal")
        mrp_production_form = Form(self.mrp_production_model)
        mrp_production_form.product_id = self.product
        self.assertEqual(mrp_production_form.bom_id, bom)
        self.assertTrue(mrp_production_form.move_raw_ids)

    def test_mrp_production_misc_bom_subcontract(self):
        """We create a BOM of subcontract type. We create a production order and assign
        the product to check that the BOM is assigned correctly."""
        bom = self._create_bom("subcontract")
        mrp_production_form = Form(self.mrp_production_model)
        mrp_production_form.product_id = self.product
        self.assertEqual(mrp_production_form.bom_id, bom)
        self.assertTrue(mrp_production_form.move_raw_ids)

    @classmethod
    def _product_replenish(cls, product, qty):
        replenish_form = Form(
            cls.env["product.replenish"].with_context(default_product_id=product.id)
        )
        replenish_form.quantity = qty
        replenish = replenish_form.save()
        replenish.launch_replenishment()

    @users("test_mrp_routings_user")
    def test_product_replenish(self):
        """We create a bill of materials of subcontract type. We run replenish and
        validate that the production order has been created with the correct BOM."""
        bom = self._create_bom("subcontract")
        mrp_bom_form = Form(bom)
        with mrp_bom_form.operation_ids.new() as operation_form:
            operation_form.name = "Test operation"
            operation_form.workcenter_id = self.workcenter
        bom = mrp_bom_form.save()
        self._product_replenish(self.product, 1)
        item = self.mrp_production_model.search([("product_id", "=", self.product.id)])
        self.assertEqual(item.bom_id, bom)
        self.assertIn(self.workcenter, item.workorder_ids.mapped("workcenter_id"))
