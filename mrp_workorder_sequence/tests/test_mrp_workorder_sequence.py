# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import Command, fields
from odoo.tests import Form

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpWorkorderSequence(TestMrpCommon):
    def setUp(self):
        super().setUp()
        self._create_bom()
        self.env["res.config.settings"].create(
            {
                "group_mrp_routings": True,
            }
        ).execute()

    def _create_bom(self):
        return self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_7_template.id,
                "product_uom_id": self.uom_unit.id,
                "product_qty": 4.0,
                "type": "normal",
                "operation_ids": [
                    Command.create(
                        {
                            "name": "Cutting Machine",
                            "workcenter_id": self.workcenter_1.id,
                            "time_cycle": 12,
                            "sequence": 1,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Weld Machine",
                            "workcenter_id": self.workcenter_1.id,
                            "time_cycle": 18,
                            "sequence": 2,
                            "bom_product_template_attribute_value_ids": [
                                Command.link(self.product_7_attr1_v1.id)
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "name": "Taking a coffee",
                            "workcenter_id": self.workcenter_1.id,
                            "time_cycle": 5,
                            "sequence": 3,
                            "bom_product_template_attribute_value_ids": [
                                Command.link(self.product_7_attr1_v2.id)
                            ],
                        }
                    ),
                ],
                "byproduct_ids": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "product_uom_id": self.product_1.uom_id.id,
                            "product_qty": 1,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_2.id,
                            "product_uom_id": self.product_2.uom_id.id,
                            "product_qty": 1,
                            "bom_product_template_attribute_value_ids": [
                                Command.link(self.product_7_attr1_v1.id)
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_3.id,
                            "product_uom_id": self.product_3.uom_id.id,
                            "product_qty": 1,
                            "bom_product_template_attribute_value_ids": [
                                Command.link(self.product_7_attr1_v2.id)
                            ],
                        }
                    ),
                ],
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_2.id,
                            "product_qty": 2,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_3.id,
                            "product_qty": 2,
                            "bom_product_template_attribute_value_ids": [
                                Command.link(self.product_7_attr1_v1.id)
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_4.id,
                            "product_qty": 2,
                            "bom_product_template_attribute_value_ids": [
                                Command.link(self.product_7_attr1_v2.id)
                            ],
                        }
                    ),
                ],
            }
        )

    def _create_order(self, product):
        mrp_order_form = Form(self.env["mrp.production"])
        mrp_order_form.product_id = product
        return mrp_order_form.save()

    def test_mrp_workorder_sequence_new_production(self):
        mrp_order = self._create_order(self.product_7_1)
        self.assertEqual(len(mrp_order.workorder_ids), 2)
        for seq, workorder in enumerate(mrp_order.workorder_ids, 1):
            self.assertEqual(workorder.sequence, seq)

    def test_mrp_workorder_sequence_new_production_new_workorder(self):
        mrp_order = self._create_order(self.product_7_1)
        self.assertEqual(len(mrp_order.workorder_ids), 2)
        max_sequence = max(mrp_order.workorder_ids.mapped("sequence"))
        mrp_order_form = Form(mrp_order)
        with mrp_order_form.workorder_ids.new() as wo_form:
            wo_form.name = "Extra operation"
            wo_form.workcenter_id = self.workcenter_1
        mrp_order = mrp_order_form.save()
        self.assertEqual(len(mrp_order.workorder_ids), 3)
        last_wo = fields.first(mrp_order.workorder_ids.sorted(reverse=True))
        self.assertEqual(last_wo.sequence, max_sequence + 1)

    def test_mrp_workorder_create_multi(self):
        """
        Test automatic sequence assignation through create override

        * WO 1: - each added operations without sequence defined
                get the next sequence after existing WOs
        * WO 2: - first added operation without sequence
                get the next sequence after existing WOs
                - second added operation with sequence defined stays unchanged
        * WO 3: - first added operation with sequence defined stays unchanged
                - second added operation without sequence defined
                get the next sequence from previous operation created
        """
        first_mrp_order = self._create_order(self.product_7_1)
        second_mrp_order = self._create_order(self.product_7_1)
        third_mrp_order = self._create_order(self.product_7_1)
        create_values = [
            {
                "name": "Extra WO 1.1",
                "production_id": first_mrp_order.id,
                "workcenter_id": self.workcenter_1.id,
                "product_uom_id": self.product_7_1.uom_id.id,
            },
            {
                "name": "Extra WO 1.2",
                "production_id": first_mrp_order.id,
                "workcenter_id": self.workcenter_1.id,
                "product_uom_id": self.product_7_1.uom_id.id,
            },
            {
                "name": "Extra WO 2.1",
                "production_id": second_mrp_order.id,
                "workcenter_id": self.workcenter_1.id,
                "product_uom_id": self.product_7_1.uom_id.id,
            },
            {
                "name": "Extra WO 2.2",
                "production_id": second_mrp_order.id,
                "workcenter_id": self.workcenter_1.id,
                "product_uom_id": self.product_7_1.uom_id.id,
                "sequence": 6,
            },
            {
                "name": "Extra WO 3.1",
                "production_id": third_mrp_order.id,
                "workcenter_id": self.workcenter_1.id,
                "sequence": 4,
                "product_uom_id": self.product_7_1.uom_id.id,
            },
            {
                "name": "Extra WO 3.2",
                "production_id": third_mrp_order.id,
                "workcenter_id": self.workcenter_1.id,
                "product_uom_id": self.product_7_1.uom_id.id,
            },
        ]
        created_wos = self.env["mrp.workorder"].create(create_values)
        expected_res = {
            "Extra WO 1.1": 3,
            "Extra WO 1.2": 4,
            "Extra WO 2.1": 3,
            "Extra WO 2.2": 6,
            "Extra WO 3.1": 4,
            "Extra WO 3.2": 5,
        }
        for wo in created_wos:
            self.assertEqual(wo.sequence, expected_res[wo.name])
