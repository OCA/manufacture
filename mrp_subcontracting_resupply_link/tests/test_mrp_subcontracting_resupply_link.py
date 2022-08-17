# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID
from odoo.tests import Form, new_test_user

from odoo.addons.test_mail.tests.common import TestMailCommon


class TestMrpSubcontractingResupplyLink(TestMailCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.subcontractor_mto = cls.env.ref(
            "mrp_subcontracting.route_resupply_subcontractor_mto"
        )
        cls.supplier = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.supplier.id,
                            "min_qty": 1,
                            "price": 10,
                        },
                    )
                ],
            }
        )
        cls.component = cls.env["product.product"].create(
            {
                "name": "Test Component",
                "route_ids": [(6, 0, [cls.subcontractor_mto.id])],
            }
        )
        cls.bom = cls._create_mrp_bom(cls)
        cls.purchase_order = cls._create_purchase_order(cls)
        cls.user = new_test_user(
            cls.env,
            login="test_user",
            groups="purchase.group_purchase_user,mrp.group_mrp_user,mrp.group_mrp_manager",
        )

    def _create_mrp_bom(self):
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product.product_tmpl_id
        mrp_bom_form.type = "subcontract"
        mrp_bom_form.subcontractor_ids.add(self.supplier)
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.component
            line_form.product_qty = 1
        return mrp_bom_form.save()

    def _create_purchase_order(self):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = self.supplier
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_qty = 1
        return order_form.save()

    def test_purchase_order_process(self):
        self.purchase_order.with_user(self.user).button_confirm()
        production = self.env["mrp.production"].search([("bom_id", "=", self.bom.id)])
        res = self.purchase_order.action_view_subcontracting_resupply()
        self.assertEqual(res["res_id"], production.picking_ids.id)
        self.assertEqual(
            production.picking_ids.subcontracting_purchase_order_id,
            self.purchase_order,
        )
        # Force flush tracking and check if messages have been created
        po_old_messages = self.purchase_order.message_ids
        picking_old_messages = production.picking_ids.message_ids
        self.flush_tracking()
        # purchase order message
        new_messages = self.purchase_order.message_ids - po_old_messages
        message = new_messages.filtered(lambda x: x.create_uid.id == SUPERUSER_ID)
        self.assertTrue(production.picking_ids.name in message.body)
        # picking order message (subcontracting_resupply_ids)
        new_messages = production.picking_ids.message_ids - picking_old_messages
        message = new_messages.filtered(lambda x: x.create_uid.id == SUPERUSER_ID)
        self.assertTrue(self.purchase_order.name in message.body)
