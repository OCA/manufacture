# Copyright 2026 FactorLibre - Daniel Amores
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.quality_control_oca.tests.test_quality_control import (
    TestQualityControlOcaBase,
)


@tagged("post_install", "-at_install")
class TestInspectionCompanyMrp(TestQualityControlOcaBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env.company
        cls.company_b = cls.env["res.company"].create({"name": "Company B"})
        cls.warehouse_b = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company_b.id)], limit=1
        )
        cls.warehouse_b.manufacture_to_resupply = True
        cls.manufacture_route = cls.warehouse_b.manufacture_pull_id.route_id
        cls.manu_type_b = cls.warehouse_b.manu_type_id
        cls.trigger_b = cls.env["qc.trigger"].search(
            [("picking_type_id", "=", cls.manu_type_b.id)]
        )
        cls.trigger_b.ensure_one()
        env_b = cls.env["product.product"].with_company(cls.company_b)
        cls.component_b = env_b.create(
            {
                "name": "Component B",
                "detailed_type": "product",
                "company_id": cls.company_b.id,
            }
        )
        cls.finished_b = env_b.create(
            {
                "name": "Finished B",
                "detailed_type": "product",
                "company_id": cls.company_b.id,
                "route_ids": [(6, 0, cls.manufacture_route.ids)],
                "qc_triggers": [
                    (
                        0,
                        0,
                        {
                            "trigger": cls.trigger_b.id,
                            "test": cls.test.id,
                            "timing": "before",
                        },
                    )
                ],
            }
        )
        cls.bom_b = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished_b.product_tmpl_id.id,
                "product_qty": 1,
                "company_id": cls.company_b.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.component_b.id, "product_qty": 1})
                ],
            }
        )
        cls.orderpoint_b = cls.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": cls.finished_b.id,
                "warehouse_id": cls.warehouse_b.id,
                "location_id": cls.warehouse_b.lot_stock_id.id,
                "company_id": cls.company_b.id,
                "route_id": cls.manufacture_route.id,
                "product_min_qty": 1,
                "product_max_qty": 5,
            }
        )

    def test_inspection_company_scheduler_without_company(self):
        """Productions confirmed by the scheduler under another active company
        generate the inspection in the production company."""
        self.env["procurement.group"].with_company(self.company_a).run_scheduler()
        production = self.env["mrp.production"].search(
            [
                ("company_id", "=", self.company_b.id),
                ("product_id", "=", self.finished_b.id),
            ]
        )
        self.assertEqual(len(production), 1, "The scheduler must create one MO")
        self.assertNotEqual(production.state, "draft")
        inspection = self.env["qc.inspection"].search(
            [("object_id", "=", "stock.move,%d" % production.move_finished_ids.id)]
        )
        self.assertEqual(len(inspection), 1, "One inspection must be created")
        self.assertEqual(inspection.company_id, self.company_b)
