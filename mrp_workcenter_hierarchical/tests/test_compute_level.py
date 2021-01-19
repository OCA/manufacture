# © 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class ComputeParentLevel(TransactionCase):
    def test_compute_low_level_workcenter(self):
        workcenter = self.env["mrp.workcenter"].create({"name": "any"})

        def get_record(string):
            return self.env.ref("mrp_workcenter_hierarchical.%s" % string)

        workcenter.write({"parent_id": get_record("workc_12").id})
        assert workcenter.parent_level_3_id == get_record("workc_123")
        assert workcenter.parent_level_2_id == get_record("workc_1234")
        assert workcenter.parent_level_1_id == get_record("workc_12345")
