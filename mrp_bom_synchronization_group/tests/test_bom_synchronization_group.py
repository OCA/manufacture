# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestBomSynchronizationGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Bom = cls.env["mrp.bom"]
        cls.Group = cls.env["mrp.bom.synchronization.group"]
        cls.Product = cls.env["product.product"]
        cls.finished_a = cls.Product.create({"name": "Finished A"})
        cls.finished_b = cls.Product.create({"name": "Finished B"})
        cls.comp_1 = cls.Product.create({"name": "Component 1"})
        cls.comp_2 = cls.Product.create({"name": "Component 2"})
        cls.comp_3 = cls.Product.create({"name": "Component 3"})
        cls.bom_a = cls._create_bom(cls.finished_a, [(cls.comp_1, 1), (cls.comp_2, 2)])
        cls.bom_b = cls._create_bom(cls.finished_b, [(cls.comp_1, 1), (cls.comp_2, 2)])

    @classmethod
    def _create_bom(cls, product, components):
        return cls.Bom.create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {"product_id": comp.id, "product_qty": qty},
                    )
                    for comp, qty in components
                ],
            }
        )

    def test_aligned_groups_not_out_of_sync(self):
        group = self.Group.create(
            {
                "name": "G1",
                "bom_ids": [(6, 0, (self.bom_a + self.bom_b).ids)],
                "synchronization_mode": "warning",
            }
        )
        self.assertFalse(group.out_of_sync)
        self.assertFalse(self.bom_a.bom_sync_out_of_sync)

    def test_detect_out_of_sync(self):
        group = self.Group.create(
            {
                "name": "G1",
                "bom_ids": [(6, 0, (self.bom_a + self.bom_b).ids)],
                "synchronization_mode": "warning",
            }
        )
        self.bom_b.bom_line_ids[0].product_qty = 5
        self.assertTrue(group.out_of_sync)
        self.assertTrue(self.bom_b.bom_sync_out_of_sync)

    def test_uom_difference_detected_and_synced(self):
        dozen = self.env.ref("uom.product_uom_dozen")
        group = self.Group.create(
            {
                "name": "G1",
                "bom_ids": [(6, 0, (self.bom_a + self.bom_b).ids)],
                "synchronization_mode": "warning",
            }
        )
        self.assertFalse(group.out_of_sync)
        line_b = self.bom_b.bom_line_ids.filtered(
            lambda line: line.product_id == self.comp_1
        )
        line_a = self.bom_a.bom_line_ids.filtered(
            lambda line: line.product_id == self.comp_1
        )
        line_b.product_uom_id = dozen
        self.assertTrue(group.out_of_sync)
        self.bom_a._synchronize_components_to(self.bom_b)
        self.assertFalse(group.out_of_sync)
        self.assertEqual(line_b.product_uom_id, line_a.product_uom_id)

    def test_manual_synchronization_preserves_operation(self):
        operation = self.env["mrp.routing.workcenter"].create(
            {
                "name": "Op B",
                "bom_id": self.bom_b.id,
                "workcenter_id": self.env.ref("mrp.mrp_workcenter_1").id,
            }
        )
        self.bom_b.bom_line_ids[0].operation_id = operation
        self.bom_a.bom_line_ids[1].product_qty = 9
        self.bom_a.bom_line_ids = [
            (0, 0, {"product_id": self.comp_3.id, "product_qty": 4})
        ]
        group = self.Group.create(
            {
                "name": "G1",
                "bom_ids": [(6, 0, (self.bom_a + self.bom_b).ids)],
                "synchronization_mode": "warning",
            }
        )
        self.assertTrue(group.out_of_sync)
        self.bom_a._synchronize_components_to(self.bom_b)
        self.assertFalse(group.out_of_sync)
        line_comp_1 = self.bom_b.bom_line_ids.filtered(
            lambda line: line.product_id == self.comp_1
        )
        self.assertEqual(line_comp_1.operation_id, operation)

    def test_default_mode_from_setting(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "mrp_bom_synchronization_group.default_synchronization_mode", "auto"
        )
        group = self.Group.create({"name": "G1"})
        self.assertEqual(group.synchronization_mode, "auto")

    def test_automatic_synchronization(self):
        group = self.Group.create(
            {
                "name": "G1",
                "bom_ids": [(6, 0, (self.bom_a + self.bom_b).ids)],
                "synchronization_mode": "auto",
            }
        )
        self.assertEqual(group.synchronization_mode, "auto")
        self.bom_a.bom_line_ids[0].product_qty = 7
        line_b = self.bom_b.bom_line_ids.filtered(
            lambda line: line.product_id == self.comp_1
        )
        self.assertEqual(line_b.product_qty, 7)
        self.assertFalse(group.out_of_sync)
