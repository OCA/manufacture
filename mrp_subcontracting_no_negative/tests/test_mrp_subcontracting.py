# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError

from .common import Common


class TestMrpSubcontracting(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.subcontracted_bom = cls._get_subcontracted_bom()
        cls.vendor = cls.env.ref("base.res_partner_12")

    def test_no_subcontractor_stock(self):
        picking = self._create_subcontractor_receipt(
            self.vendor, self.subcontracted_bom
        )
        self.assertEqual(picking.state, "assigned")
        # No component in the subcontractor location
        with self.assertRaisesRegex(UserError, "Unable to reserve"):
            picking.action_record_components()
        # Try again once the subcontractor received the components
        self._update_stock_component_qty(
            bom=self.subcontracted_bom,
            location=self.vendor.property_stock_subcontractor,
        )
        picking.action_record_components()

    def test_with_subcontractor_stock(self):
        # Subcontractor has components before we create the receipt
        self._update_stock_component_qty(
            bom=self.subcontracted_bom,
            location=self.vendor.property_stock_subcontractor,
        )
        picking = self._create_subcontractor_receipt(
            self.vendor, self.subcontracted_bom
        )
        self.assertEqual(picking.state, "assigned")
        picking.action_record_components()
