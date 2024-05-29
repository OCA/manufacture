# © 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import TransactionCase


class ComputeParentLevel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.workc_12 = cls.env.ref("mrp_workcenter_hierarchical.workc_12")
        cls.workc_123 = cls.env.ref("mrp_workcenter_hierarchical.workc_123")
        cls.workc_1234 = cls.env.ref("mrp_workcenter_hierarchical.workc_1234")
        cls.workc_12345 = cls.env.ref("mrp_workcenter_hierarchical.workc_12345")

    def test_compute_low_level_workcenter(self):
        workcenter = self.env["mrp.workcenter"].create({"name": "any"})

        workcenter.write({"parent_id": self.workc_12.id})
        assert workcenter.parent_level_3_id == self.workc_123
        assert workcenter.parent_level_2_id == self.workc_1234
        assert workcenter.parent_level_1_id == self.workc_12345

    def test_compute_hight_level_workcenter(self):
        # test high level has parent_level fields set
        self.assertEqual(self.workc_12345.parent_level_1_id, self.workc_12345)
        self.assertEqual(self.workc_12345.parent_level_2_id, self.workc_12345)
        self.assertEqual(self.workc_12345.parent_level_3_id, self.workc_12345)

        self.assertEqual(self.workc_1234.parent_level_1_id, self.workc_12345)
        self.assertEqual(self.workc_1234.parent_level_2_id, self.workc_1234)
        self.assertEqual(self.workc_1234.parent_level_3_id, self.workc_1234)

        self.workc_12345.company_id.workcenter_parent_level_empty = True
        # test parent level of high parent is left empty if setting is set on company
        # level
        self.assertFalse(self.workc_12345.parent_level_1_id)
        self.assertFalse(self.workc_12345.parent_level_2_id)
        self.assertFalse(self.workc_12345.parent_level_2_id)

        self.assertEqual(self.workc_1234.parent_level_1_id, self.workc_12345)
        self.assertFalse(self.workc_1234.parent_level_2_id)
        self.assertFalse(self.workc_1234.parent_level_3_id)

        self.assertEqual(self.workc_123.parent_level_1_id, self.workc_12345)
        self.assertEqual(self.workc_123.parent_level_2_id, self.workc_1234)
        self.assertFalse(self.workc_123.parent_level_3_id)

    def test_switch_workcenter(self):
        # take a MO with an operation
        self.env["mrp.routing.workcenter"].with_context(active_test=False).search(
            []
        ).active = True
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.env.ref("mrp.product_product_computer_desk_head").id,
            }
        )
        mo.action_confirm()
        mo2 = mo.copy()
        mo2.action_confirm()
        wos = mo.workorder_ids + mo2.workorder_ids

        ctx = {"active_model": "mrp.workorder", "active_ids": wos.ids}
        # the default wworkcenter does not belong to any group
        with self.assertRaises(exceptions.UserError):
            self.env["switch.workcenter"].with_context(**ctx).create({})

        # set workcenter with group
        wos.write({"workcenter_id": self.workc_12345.id})
        wizard = (
            self.env["switch.workcenter"]
            .with_context(**ctx)
            .create({"workcenter_id": self.workc_123.id})
        )
        # used in view
        self.assertEqual(
            self.workc_12345.parent_level_1_id, wizard.parent_workcenter_id
        )
        wizard.switch_workcenter()
        self.assertEqual(wos.workcenter_id.id, self.workc_123.id)
