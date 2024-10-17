# Copyright (C) 2024, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestMrpException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Useful models
        cls.MrpOrder = cls.env["mrp.production"]
        cls.StockMove = cls.env["stock.move"]
        cls.product_id_1 = cls.env.ref("product.product_product_6")
        cls.product_id_2 = cls.env.ref("product.product_product_7")
        cls.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        cls.mrp_exception_confirm = cls.env["mrp.exception.confirm"]
        cls.archived_finish_product = cls.env.ref(
            "mrp_exception.excep_mo_archived_finish_product"
        )
        cls.product_component_archived = cls.env.ref(
            "mrp_exception.sm_excep_product_component_archived"
        )
        cls.mo_vals = {
            "product_id": cls.product_id_1.id,
            "move_raw_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.product_id_2.id,
                        "product_uom_qty": 5.0,
                    },
                ),
            ],
        }

    def test01_mrp_order_exception(self):
        self.archived_finish_product.active = True
        self.product_component_archived.active = True
        self.mo = self.MrpOrder.create(self.mo_vals.copy())

        # archived finished product
        self.product_id_1.active = False
        self.assertEqual(self.mo.product_id.active, False)

        self.MrpOrder.test_all_archived_finish_product()
        self.assertEqual(self.mo.product_id.active, False)
        # Set ignore_exception flag  (Done after ignore is selected at wizard)
        self.mo.ignore_exception = True
        self.mo.product_id.active = True
        self.mo.detect_exceptions()
        self.assertEqual(self.mo.product_id.active, True)

        # Add a order line to test after PO is confirmed
        field_onchange = self.MrpOrder._onchange_spec()
        self.product_id_2.active = False
        self.assertEqual(field_onchange.get("move_raw_ids"), "1")
        self.mo.write(
            {
                "move_raw_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_2.id,
                            "product_uom_qty": 5.0,
                        },
                    )
                ]
            }
        )
        self.mo.detect_exceptions()
        self.mo.ignore_exception = True
        self.assertTrue(self.mo.ignore_exception)

        # Simulation the opening of the wizard purchase_exception_confirm and
        # set ignore_exception to True
        mo_except_confirm = self.mrp_exception_confirm.with_context(
            active_id=self.mo.id,
            active_ids=[self.mo.id],
            active_model=self.mo._name,
        ).create({"ignore": True})
        mo_except_confirm.action_confirm()

    def test02_confirm_mrp_fail_by_domain(self):
        self.exception_domain = self.env["exception.rule"].create(
            {
                "name": "Archived MO Finish Product",
                "sequence": 11,
                "model": "mrp.production",
                "domain": "[('product_id.active', '=', False)]",
                "exception_type": "by_domain",
            }
        )
        self.mo = self.MrpOrder.create(self.mo_vals.copy())
        self.product_id_1.active = False
        exception_action = self.mo.action_confirm()
        self.assertEqual(exception_action.get("res_model"), "mrp.exception.confirm")
        self.assertTrue(self.mo.exceptions_summary)
        self.assertTrue(self.mo.exception_ids)

    def test03_call_mrp_method(self):
        self.MrpOrder._reverse_field()
        self.mo = self.MrpOrder.create(self.mo_vals.copy())
        self.mo.move_raw_ids[0].write({"product_id": False})
        self.mo.onchange_ignore_exception()
