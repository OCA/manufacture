# © 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class ComputeParentLevel(TransactionCase):
    def test_compute_parent_level0(self):
        workcenter = self.env["mrp.workcenter"].create(
            {
                "name": "New Assembly",
                "calendar_id": self.env.ref("resource.timesheet_group1").id,
                "capacity_per_cycle": 5,
                "time_cycle": 1,
                "time_start": 0.1,
                "time_stop": 0.1,
                "time_efficiency": 0.87,
                "product_id": self.env.ref("product.product_assembly").id,
                "costs_hour": 0,
                "costs_hour_account_id": self.env.ref("mrp.account_assembly_hours").id,
                "costs_cycle": 0.05,
                "costs_cycle_account_id": self.env.ref("mrp.account_assembly_cycle").id,
            }
        )
        workcenter_child = self.env.ref("mrp_workcenter_hierarchical.mrp_workcenter_A")
        workcenter_child.write({"parent_id": workcenter.id})
        self.assertEqual(workcenter.parent_level_1_id, workcenter)

    def test_compute_parent_level1(self):
        workcenter_child = self.env.ref("mrp_workcenter_hierarchical.mrp_workcenter_E")
        workcenter_parent = self.env.ref(
            "mrp_workcenter_hierarchical.mrp_workcenter_top"
        )
        workcenter_child.write({"parent_id": workcenter_parent.id})
        self.assertEqual(workcenter_child.parent_level_1_id, workcenter_parent)

    def test_compute_parent_level2(self):
        workcenter_child = self.env.ref("mrp_workcenter_hierarchical.mrp_workcenter_A")
        workcenter_parent1 = self.env.ref(
            "mrp_workcenter_hierarchical.mrp_workcenter_top"
        )
        workcenter_parent2 = self.env.ref("mrp.mrp_workcenter_0")
        workcenter_child.write({"parent_id": workcenter_parent2.id})
        self.assertEqual(workcenter_child.parent_level_2_id, workcenter_parent2)
        self.assertEqual(workcenter_child.parent_level_1_id, workcenter_parent1)

    def test_compute_parent_level3(self):
        workcenter_child = self.env.ref("mrp_workcenter_hierarchical.mrp_workcenter_B")
        workcenter_parent1 = self.env.ref(
            "mrp_workcenter_hierarchical.mrp_workcenter_top"
        )
        workcenter_parent2 = self.env.ref(
            "mrp_workcenter_hierarchical.mrp_workcenter_2"
        )
        workcenter_parent3 = self.env.ref(
            "mrp_workcenter_hierarchical.mrp_workcenter_A"
        )
        workcenter_child.write({"parent_id": workcenter_parent3.id})
        self.assertEqual(workcenter_child.parent_level_3_id, workcenter_parent3)
        self.assertEqual(workcenter_child.parent_level_2_id, workcenter_parent2)
        self.assertEqual(workcenter_child.parent_level_1_id, workcenter_parent1)

    def test_compute_parent_level3_bis(self):
        workcenter_child = self.env.ref("mrp_workcenter_hierarchical.mrp_workcenter_C")
        workcenter_parent3 = self.env.ref(
            "mrp_workcenter_hierarchical.mrp_workcenter_A"
        )
        workcenter_parent4 = self.env.ref(
            "mrp_workcenter_hierarchical.mrp_workcenter_B"
        )
        workcenter_parent4.write({"parent_id": workcenter_parent3.id})
        workcenter_child.write({"parent_id": workcenter_parent4.id})
        self.assertEqual(workcenter_child.parent_id, workcenter_parent4)
