# © 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import SavepointCase


class ComputeParentLevel(SavepointCase):
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

    def test_switch_workcenter(self):
        # take a MO with an operation
        mo = self.env.ref("mrp.mrp_production_3")
        mo2 = mo.copy()
        mo2.action_confirm()
        wos = mo.workorder_ids + mo2.workorder_ids

        ctx = {"active_model": "mrp.workorder", "active_ids": wos.ids}
        # the default wworkcenter does not belong to any group
        with self.assertRaises(exceptions.UserError):
            self.env["switch.workcenter"].with_context(ctx).create({})

        # set workcenter with group
        wos.write({"workcenter_id": self.workc_12345.id})
        wizard = (
            self.env["switch.workcenter"]
            .with_context(ctx)
            .create({"workcenter_id": self.workc_123.id})
        )
        # used in view
        self.assertEqual(
            self.workc_12345.parent_level_1_id, wizard.parent_workcenter_id
        )
        wizard.switch_workcenter()
        self.assertEqual(wos.workcenter_id.id, self.workc_123.id)
