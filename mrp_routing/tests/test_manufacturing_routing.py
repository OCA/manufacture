# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase

from ..models.mrp_routing_workcenter_template import FIELDS_TO_SYNC


class TestRestrictLot(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_obj = cls.env["product.product"]
        cls.bom_obj = cls.env["mrp.bom"]
        cls.bom_line_obj = cls.env["mrp.bom.line"]
        cls.routing_obj = cls.env["mrp.routing"]
        cls.workcenter_obj = cls.env["mrp.workcenter"]
        cls.routing_workcenter_obj = cls.env["mrp.routing.workcenter"]
        cls.routing_workcenter_template_obj = cls.env["mrp.routing.workcenter.template"]

        # Create products:
        cls.product_1 = cls.product_obj.create({"name": "TEST 01", "type": "product"})
        cls.product_2 = cls.product_obj.create({"name": "TEST 02", "type": "product"})
        cls.product_3 = cls.product_obj.create({"name": "TEST 03", "type": "product"})
        cls.component_1 = cls.product_obj.create({"name": "RM 01", "type": "product"})
        cls.component_2 = cls.product_obj.create({"name": "RM 02", "type": "product"})
        # Create Bills of Materials:
        cls.bom_1 = cls.bom_obj.create(
            {"product_tmpl_id": cls.product_1.product_tmpl_id.id}
        )
        cls.line_1_1 = cls.bom_line_obj.create(
            {
                "product_id": cls.component_1.id,
                "bom_id": cls.bom_1.id,
                "product_qty": 2.0,
            }
        )
        cls.line_1_2 = cls.bom_line_obj.create(
            {
                "product_id": cls.component_2.id,
                "bom_id": cls.bom_1.id,
                "product_qty": 5.0,
            }
        )
        cls.bom_2 = cls.bom_obj.create(
            {"product_tmpl_id": cls.product_1.product_tmpl_id.id}
        )
        cls.line_2_1 = cls.bom_line_obj.create(
            {
                "product_id": cls.component_1.id,
                "bom_id": cls.bom_2.id,
                "product_qty": 2.0,
            }
        )
        cls.line_2_2 = cls.bom_line_obj.create(
            {
                "product_id": cls.component_2.id,
                "bom_id": cls.bom_2.id,
                "product_qty": 5.0,
            }
        )
        cls.bom_3 = cls.bom_obj.create(
            {"product_tmpl_id": cls.product_1.product_tmpl_id.id}
        )
        cls.line_3_1 = cls.bom_line_obj.create(
            {
                "product_id": cls.component_1.id,
                "bom_id": cls.bom_3.id,
                "product_qty": 2.0,
            }
        )
        cls.line_3_2 = cls.bom_line_obj.create(
            {
                "product_id": cls.component_2.id,
                "bom_id": cls.bom_3.id,
                "product_qty": 5.0,
            }
        )
        # Create Routing
        cls.workcenter_1 = cls.env.ref("mrp.mrp_workcenter_1")
        cls.workcenter_2 = cls.env.ref("mrp.mrp_workcenter_2")
        cls.workcenter_3 = cls.env.ref("mrp.mrp_workcenter_3")
        cls.operation_template_1 = cls.routing_workcenter_template_obj.create(
            {
                "workcenter_id": cls.workcenter_1.id,
                "name": "Operation 1",
                "time_cycle_manual": 60,
                "sequence": 5,
                "worksheet_type": "text",
                "on_template_change": "sync",
            }
        )
        cls.operation_template_2 = cls.routing_workcenter_template_obj.create(
            {
                "workcenter_id": cls.workcenter_2.id,
                "name": "Operation 2",
                "time_cycle_manual": 120,
                "sequence": 10,
                "worksheet_type": "text",
                "on_template_change": "sync",
            }
        )
        cls.operation_template_3 = cls.routing_workcenter_template_obj.create(
            {
                "workcenter_id": cls.workcenter_3.id,
                "name": "Operation 3",
                "time_cycle_manual": 180,
                "sequence": 15,
                "worksheet_type": "text",
                "on_template_change": "sync",
            }
        )
        cls.operation_template_4 = cls.routing_workcenter_template_obj.create(
            {
                "workcenter_id": cls.workcenter_2.id,
                "name": "Operation 4",
                "time_cycle_manual": 150,
                "sequence": 15,
                "worksheet_type": "text",
                "on_template_change": "nothing",
            }
        )
        cls.routing_1 = cls.routing_obj.create(
            {
                "name": "Routing 1",
                "operation_ids": [
                    (
                        6,
                        0,
                        [
                            cls.operation_template_1.id,
                            cls.operation_template_2.id,
                            cls.operation_template_3.id,
                            cls.operation_template_4.id,
                        ],
                    )
                ],
            }
        )

    def test_01_sync_onchange_predefined_operations(self):
        self.bom_1.routing_id = self.routing_1.id
        self.bom_1.onchange_routing_id()
        self.assertEqual(
            self.bom_1.operation_ids.mapped("template_id").ids,
            self.routing_1.operation_ids.ids,
        )
        for operation in self.bom_1.operation_ids:
            for field_to_check in FIELDS_TO_SYNC:
                # When is setted as predefined,
                # all operations are in synced mode
                if field_to_check == "on_template_change":
                    continue
                self.assertEqual(
                    operation[field_to_check], operation.template_id[field_to_check]
                )

    def test_02_sync_templates_changes_by_bom(self):
        self.bom_1.routing_id = self.routing_1.id
        self.bom_1.onchange_routing_id()
        self.bom_2.routing_id = self.routing_1.id
        self.bom_2.onchange_routing_id()
        self.operation_template_1.write(
            {
                "sequence": 30,
                "time_cycle_manual": 100,
            }
        )
        for operation in self.routing_workcenter_obj.search(
            [("template_id", "=", self.operation_template_1.id)]
        ):
            self.assertEqual(operation.sequence, self.operation_template_1.sequence)
            self.assertEqual(
                operation.time_cycle_manual, self.operation_template_1.time_cycle_manual
            )
        # Operation 4 is setted that not sync on changes,
        # but operations was created by predefined operations
        self.operation_template_4.write(
            {
                "name": "New Operation Name",
                "time_cycle_manual": 100,
            }
        )
        for operation in self.routing_workcenter_obj.search(
            [("template_id", "=", self.operation_template_4.id)]
        ):
            self.assertEqual(operation.name, self.operation_template_4.name)
            self.assertEqual(
                operation.time_cycle_manual, self.operation_template_4.time_cycle_manual
            )

        # On delete all operations related should be deleted
        self.assertEqual(
            2,
            self.routing_workcenter_obj.search_count(
                [("template_id", "=", self.operation_template_3.id)]
            ),
        )
        self.operation_template_3.unlink()
        self.assertEqual(
            0,
            self.routing_workcenter_obj.search_count(
                [("template_id", "=", self.operation_template_3.id)]
            ),
        )

    def test_03_sync_templates_changes_manual_creation(self):
        operation_1 = self.routing_workcenter_obj.create(
            {
                "workcenter_id": self.workcenter_1.id,
                "name": "Operation without name",
                "time_cycle_manual": 150,
                "sequence": 15,
                "worksheet_type": "text",
                "bom_id": self.bom_3.id,
            }
        )
        operation_1.write(
            {
                "template_id": self.operation_template_1,
            }
        )
        operation_1.onchange_template_id()
        for field_to_check in FIELDS_TO_SYNC:
            self.assertEqual(
                operation_1[field_to_check], operation_1.template_id[field_to_check]
            )
        operation_2 = self.routing_workcenter_obj.create(
            {
                "workcenter_id": self.workcenter_2.id,
                "name": "Operation 4",
                "time_cycle_manual": 20,
                "sequence": 5,
                "worksheet_type": "text",
                "bom_id": self.bom_3.id,
            }
        )
        operation_2.write(
            {
                "template_id": self.operation_template_4,
            }
        )
        operation_2.onchange_template_id()
        self.operation_template_4.write({"name": "New Name Operation 4"})
        self.assertNotEqual(operation_2.name, self.operation_template_4.name)

    def test_04_sync_templates_routing_changes(self):
        self.bom_1.routing_id = self.routing_1.id
        self.bom_1.onchange_routing_id()
        self.bom_2.routing_id = self.routing_1.id
        self.bom_2.onchange_routing_id()
        self.routing_1.write(
            {
                "operation_ids": [
                    (
                        6,
                        0,
                        [
                            self.operation_template_1.id,
                            self.operation_template_2.id,
                        ],
                    )
                ]
            }
        )
        self.assertNotIn(
            self.operation_template_4.id,
            self.bom_1.operation_ids.mapped("template_id").ids,
        )
        self.assertNotIn(
            self.operation_template_4.id,
            self.bom_2.operation_ids.mapped("template_id").ids,
        )
        self.routing_1.write(
            {
                "operation_ids": [
                    (
                        6,
                        0,
                        [
                            self.operation_template_1.id,
                            self.operation_template_2.id,
                            self.operation_template_4.id,
                        ],
                    )
                ]
            }
        )
        self.assertIn(
            self.operation_template_4.id,
            self.bom_1.operation_ids.mapped("template_id").ids,
        )
        self.assertIn(
            self.operation_template_4.id,
            self.bom_2.operation_ids.mapped("template_id").ids,
        )
