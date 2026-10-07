# Copyright 2026 FactorLibre - Daniel Amores
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.quality_control_oca.tests.test_quality_control import (
    TestQualityControlOcaBase,
)


@tagged("post_install", "-at_install")
class TestInspectionCompanyStock(TestQualityControlOcaBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env.company
        cls.company_b = cls.env["res.company"].create({"name": "Company B"})
        cls.warehouse_b = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company_b.id)], limit=1
        )
        cls.picking_type_b = cls.warehouse_b.out_type_id
        cls.trigger_b = cls.env["qc.trigger"].search(
            [("picking_type_id", "=", cls.picking_type_b.id)]
        )
        cls.trigger_b.ensure_one()
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Stock product B",
                "detailed_type": "product",
                "company_id": cls.company_b.id,
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
        cls.user_ab = cls.env["res.users"].create(
            {
                "name": "User A and B",
                "login": "user_ab_inspection_company",
                "company_id": cls.company_a.id,
                "company_ids": [(6, 0, (cls.company_a | cls.company_b).ids)],
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("stock.group_stock_user").id,
                            cls.env.ref(
                                "quality_control_oca.group_quality_control_user"
                            ).id,
                        ],
                    )
                ],
            }
        )
        cls.user_b = cls.env["res.users"].create(
            {
                "name": "User B",
                "login": "user_b_inspection_company",
                "company_id": cls.company_b.id,
                "company_ids": [(6, 0, cls.company_b.ids)],
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("stock.group_stock_user").id,
                            cls.env.ref(
                                "quality_control_oca.group_quality_control_user"
                            ).id,
                        ],
                    )
                ],
            }
        )

    def test_inspection_company_from_move_other_company(self):
        """Confirming a picking of company B with company A active creates the
        inspection in company B."""
        customers = self.env.ref("stock.stock_location_customers")
        stock_location = self.picking_type_b.default_location_src_id
        env_a = (
            self.env["stock.picking"]
            .with_user(self.user_ab)
            .with_context(allowed_company_ids=[self.company_a.id, self.company_b.id])
        )
        picking = env_a.create(
            {
                "picking_type_id": self.picking_type_b.id,
                "location_id": stock_location.id,
                "location_dest_id": customers.id,
                "company_id": self.company_b.id,
                "move_ids_without_package": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_b.name,
                            "product_id": self.product_b.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_b.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customers.id,
                            "company_id": self.company_b.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        inspection = self.env["qc.inspection"].search([("picking_id", "=", picking.id)])
        self.assertEqual(len(inspection), 1, "One inspection must be created")
        self.assertEqual(inspection.company_id, self.company_b)
        visible_inspection = (
            self.env["qc.inspection"]
            .with_user(self.user_b)
            .search([("picking_id", "=", picking.id)])
        )
        self.assertEqual(visible_inspection, inspection)
