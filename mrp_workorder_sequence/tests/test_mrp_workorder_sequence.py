# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import Command
from odoo.tests import Form

from odoo.addons.mrp.tests.test_bom import TestBoM


class TestMrpWorkorderSequence(TestBoM):
    def test_mrp_workorder_sequence(self):
        self.env["mrp.bom"].create(
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
        mrp_order_form = Form(self.env["mrp.production"])
        mrp_order_form.product_id = self.product_7_3
        mrp_order = mrp_order_form.save()
        for workorder in mrp_order.workorder_ids:
            self.assertEqual(workorder.sequence, workorder.operation_id.sequence)
