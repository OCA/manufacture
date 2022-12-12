# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, TransactionCase


class TestSearch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.component = cls.env["product.product"].create(
            {"name": "Component", "type": "product"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )
        cls.product_bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_qty": 1.0,
                "product_uom_id": cls.product.uom_id.id,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.component.id,
                            "product_qty": 1.0,
                            "product_uom_id": cls.component.uom_id.id,
                        }
                    )
                ],
            }
        )
        # Create some initial stocks
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"].create(
            {
                "product_id": cls.component.id,
                "product_uom_id": cls.component.uom_id.id,
                "location_id": cls.location_stock.id,
                "quantity": 10.00,
            }
        )
        # Create some manufacturing orders
        cls.mo_draft = cls._create_mo(confirm=False)
        cls.mo_confirm = cls._create_mo(confirm=True)
        cls.mo_unavailable = cls._create_mo(quantity=1000.0, confirm=True)

    @classmethod
    def _create_mo(cls, product=None, bom=None, quantity=1.0, confirm=False):
        if product is None:
            product = cls.product
        if bom is None:
            bom = cls.product_bom
        mo_form = Form(cls.env["mrp.production"])
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = quantity
        mo_form.product_uom_id = product.uom_id
        mo = mo_form.save()
        if confirm:
            mo.action_confirm()
        return mo

    def test_search_is_set(self):
        records = self.env["mrp.production"].search(
            [
                ("product_id", "=", self.product.id),
                ("components_availability_state", "!=", False),
            ]
        )
        self.assertEqual(records, self.mo_confirm + self.mo_unavailable)

    def test_search_is_not_set(self):
        records = self.env["mrp.production"].search(
            [
                ("product_id", "=", self.product.id),
                ("components_availability_state", "=", False),
            ]
        )
        self.assertEqual(records, self.mo_draft)

    def test_search_is_available(self):
        records = self.env["mrp.production"].search(
            [
                ("product_id", "=", self.product.id),
                ("components_availability_state", "=", "available"),
            ]
        )
        self.assertEqual(records, self.mo_confirm)

    def test_search_is_not_available(self):
        records = self.env["mrp.production"].search(
            [
                ("product_id", "=", self.product.id),
                ("components_availability_state", "!=", "available"),
            ]
        )
        self.assertEqual(records, self.mo_draft + self.mo_unavailable)
