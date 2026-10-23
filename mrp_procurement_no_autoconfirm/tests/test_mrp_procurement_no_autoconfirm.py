# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.base.tests.common import BaseCommon


class TestMrpProcurementNoAutoconfirm(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        component = cls.env["product.product"].create(
            {"name": "Test Component", "is_storable": True}
        )
        finished = cls.env["product.product"].create(
            {"name": "Test Finished Product", "is_storable": True}
        )
        bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": component.id, "product_qty": 1.0})
                ],
            }
        )
        cls.production = cls.env["mrp.production"].create(
            {
                "product_id": finished.id,
                "bom_id": bom.id,
                "product_qty": 2.0,
            }
        )
        parent_production = cls.env["mrp.production"].create(
            {"product_id": component.id, "product_qty": 1.0}
        )
        cls.env["stock.move"].create(
            {
                "name": "Test dest move",
                "product_id": finished.id,
                "product_uom_qty": 1.0,
                "product_uom": finished.uom_id.id,
                "location_id": cls.production.location_src_id.id,
                "location_dest_id": cls.production.location_dest_id.id,
                "created_production_id": cls.production.id,
                "raw_material_production_id": parent_production.id,
            }
        )

    def test_setting_enabled_prevents_auto_confirm_for_child_mo(self):
        self.env.company.mrp_procurement_no_autoconfirm = True
        self.assertFalse(
            self.env["stock.rule"]._should_auto_confirm_procurement_mo(self.production)
        )

    def test_setting_enabled_does_not_affect_non_child_mo(self):
        self.env.company.mrp_procurement_no_autoconfirm = True
        standalone = self.env["mrp.production"].create(
            {
                "product_id": self.production.product_id.id,
                "bom_id": self.production.bom_id.id,
                "product_qty": 1.0,
            }
        )
        self.assertTrue(
            self.env["stock.rule"]._should_auto_confirm_procurement_mo(standalone)
        )

    def test_setting_disabled_delegates_to_core(self):
        self.env.company.mrp_procurement_no_autoconfirm = False
        self.assertTrue(
            self.env["stock.rule"]._should_auto_confirm_procurement_mo(self.production)
        )
