# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase


@tagged("post_install", "-at_install")
class TestMrpSetQuantityToReservation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "product"}
        )
        cls.component = cls.env["product.product"].create(
            {"name": "Test component", "type": "product"}
        )
        updatate_qty_data = cls.component.action_update_quantity_on_hand()
        stock_quant_form = Form(
            cls.env["stock.quant"].with_context(**updatate_qty_data["context"]),
            view="stock.view_stock_quant_tree_inventory_editable",
        )
        stock_quant_form.inventory_quantity = 20
        quant = stock_quant_form.save()
        quant.action_apply_inventory()
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_uom_id": cls.product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.bom.id, "product_id": cls.component.id, "product_qty": 2}
        )

    def test_set_quantity_to_reservation(self):
        mrp_form = Form(self.env["mrp.production"])
        mrp_form.product_id = self.product
        mrp = mrp_form.save()
        self.assertEqual(mrp.bom_id, self.bom)
        mrp.action_confirm()
        mrp.action_set_quantities_to_reservation()
        self.assertEqual(mrp.move_raw_ids.quantity_done, 2)
        mrp_form = Form(self.env["mrp.production"])
        mrp_form.product_id = self.product
        mrp_form.product_qty = 10
        mrp_2 = mrp_form.save()
        mrp_2.action_confirm()
        mrp_2.action_set_quantities_to_reservation()
        self.assertEqual(mrp_2.move_raw_ids.quantity_done, 18)
