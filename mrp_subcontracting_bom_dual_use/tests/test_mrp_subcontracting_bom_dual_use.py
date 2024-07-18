# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, common


class TestMrpSubcontractingBomDualUse(common.SavepointCase):
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

    def _create_bom(self, bom_type):
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product.product_tmpl_id
        mrp_bom_form.type = bom_type
        if bom_type == "subcontract":
            mrp_bom_form.subcontractor_ids.add(self.partner)
            mrp_bom_form.allow_in_regular_production = True
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.component_a
            line_form.product_qty = 1
        with mrp_bom_form.operation_ids.new() as operation_form:
            operation_form.name = "Test operation"
            operation_form.workcenter_id = self.workcenter
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
        self.assertTrue(mrp_production_form.workorder_ids)

    def _product_replenish(self, product, qty):
        replenish_form = Form(
            self.env["product.replenish"].with_context(default_product_id=product.id)
        )
        replenish_form.quantity = qty
        replenish = replenish_form.save()
        replenish.launch_replenishment()

    def test_product_replenish(self):
        """We create a bill of materials of subcontract type. We run replenish and
        validate that the production order has been created with the correct BOM."""
        bom = self._create_bom("subcontract")
        self._product_replenish(self.product, 1)
        item = self.mrp_production_model.search([("product_id", "=", self.product.id)])
        self.assertEqual(item.bom_id, bom)
        self.assertIn(self.workcenter, item.workorder_ids.mapped("workcenter_id"))

    def test_picking_subcontract(self):
        self._create_bom("subcontract")
        picking_form = Form(
            self.env["stock.picking"].with_context(
                default_picking_type_id=self.env.ref("stock.picking_type_in").id,
            )
        )
        picking_form.partner_id = self.partner
        with picking_form.move_ids_without_package.new() as move_form:
            move_form.product_id = self.product
            move_form.product_uom_qty = 1
        picking = picking_form.save()
        picking.action_confirm()
        item = self.mrp_production_model.search([("product_id", "=", self.product.id)])
        self.assertIn(self.workcenter, item.workorder_ids.mapped("workcenter_id"))
