# Copyright 2023 Quartile (https://www.quartile.co)
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


class TestMrpSubcontractingSkipNoNegative(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_stock_no_negative=True,
            )
        )
        warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = warehouse.lot_stock_id
        cls.subcontractor_location = cls.env["stock.location"].create(
            {
                "name": "Subcontractor 1",
                "usage": "internal",
                "location_id": warehouse.view_location_id.id,
            }
        )
        cls.subcontractor_partner1 = cls.env["res.partner"].create(
            {
                "name": "Subcontractor 1",
                "company_type": "company",
                "property_stock_subcontractor": cls.subcontractor_location.id,
            }
        )
        cls.comp1 = cls.env["product.product"].create(
            {"name": "Component1", "is_storable": True}
        )
        cls.comp2 = cls.env["product.product"].create(
            {"name": "Component2", "is_storable": True}
        )
        cls.finished = cls.env["product.product"].create(
            {"name": "Finished product", "is_storable": True}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished.product_tmpl_id.id,
                "product_id": cls.finished.id,
                "product_uom_id": cls.finished.uom_id.id,
                "type": "subcontract",
                "subcontractor_ids": [
                    Command.set([cls.subcontractor_partner1.id]),
                ],
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.comp1.id,
                            "product_uom_id": cls.comp1.uom_id.id,
                            "product_qty": 1.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.comp2.id,
                            "product_uom_id": cls.comp2.uom_id.id,
                            "product_qty": 1.0,
                        }
                    ),
                ],
            }
        )
        picking_form = Form(cls.env["stock.picking"])
        picking_form.picking_type_id = cls.env.ref("stock.picking_type_in")
        picking_form.partner_id = cls.subcontractor_partner1
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = cls.finished
            move.product_uom_qty = 1.0
        cls.subcontracting_receipt = picking_form.save()

    def _create_stock_quant(self, product, qty):
        self.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": self.subcontractor_location.id,
                "quantity": qty,
            }
        )

    @mute_logger("odoo.models.unlink")
    def test_mrp_subcontracting_no_stock_components(self):
        """No stock at subcontractor: fail first on comp1, then on comp2."""
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        with self.assertRaises(ValidationError) as e1:
            self.subcontracting_receipt.sudo().button_validate()
        self.assertIn("Component1", str(e1.exception))
        self._create_stock_quant(self.comp1, 10)
        with self.assertRaises(ValidationError) as e2:
            self.subcontracting_receipt.sudo().button_validate()
        self.assertIn("Component2", str(e2.exception))
        self._create_stock_quant(self.comp2, 10)
        self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(self.subcontracting_receipt.state, "done")

    def test_mrp_subcontracting_stock_components(self):
        """Both components in stock -> subcontracting receipt OK."""
        self._create_stock_quant(self.comp1, 10)
        self._create_stock_quant(self.comp2, 10)
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(self.subcontracting_receipt.state, "done")

    def test_mrp_subcontracting_allow_negative_stock(self):
        """If subcontractor location allows negative stock, receipt is allowed."""
        self.subcontractor_location.allow_negative_stock = True
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(self.subcontracting_receipt.state, "done")

    def test_mrp_subcontracting_with_normal_product(self):
        """Extra normal product on the picking shouldn't break the flow."""
        another_product = self.env["product.product"].create(
            {
                "name": "Another Product",
                "is_storable": True,
            }
        )
        self.env["stock.move"].create(
            {
                "picking_id": self.subcontracting_receipt.id,
                "product_id": another_product.id,
                "name": another_product.name,
                "product_uom": another_product.uom_id.id,
                "product_uom_qty": 1.0,
                "location_id": self.subcontracting_receipt.location_id.id,
                "location_dest_id": self.subcontracting_receipt.location_dest_id.id,
            }
        )
        self._create_stock_quant(self.comp1, 10)
        self._create_stock_quant(self.comp2, 10)
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(self.subcontracting_receipt.state, "done")
        products = self.subcontracting_receipt.move_ids.mapped("product_id")
        self.assertIn(self.finished, products)
        self.assertIn(another_product, products)
        for move in self.subcontracting_receipt.move_ids:
            self.assertEqual(move.quantity, 1.0)
