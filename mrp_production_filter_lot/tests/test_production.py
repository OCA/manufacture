# Copyright 2025 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import tests
from odoo.tools.safe_eval import safe_eval

from odoo.addons.mrp.tests.common import TestMrpCommon


@tests.tagged("post_install", "-at_install")
class TestProduction(TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.other_stock_location = cls.stock_location.copy(
            default={
                "name": "Test other stock",
            },
        )
        cls.product, cls.component = cls.env["product.product"].create(
            [
                {
                    "name": "Test Product",
                },
                {
                    "name": "Test Component",
                    "tracking": "lot",
                    "type": "product",
                },
            ]
        )
        cls.component_stock_lot, cls.component_other_stock_lot = cls.env[
            "stock.production.lot"
        ].create(
            [
                {
                    "name": "Test Lot in Stock",
                    "product_id": cls.component.id,
                },
                {
                    "name": "Test Lot in Other Stock",
                    "product_id": cls.component.id,
                },
            ]
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.component,
            cls.stock_location,
            100,
            lot_id=cls.component_stock_lot,
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.component,
            cls.other_stock_location,
            100,
            lot_id=cls.component_other_stock_lot,
        )

        production_form = tests.Form(cls.env["mrp.production"])
        production_form.product_id = cls.product
        production_form.bom_id = cls.make_bom(cls.product, cls.component)
        cls.production = production_form.save()
        cls.production.action_confirm()
        cls.production.action_assign()

    @classmethod
    def _get_lots_domain(cls, move_line):
        """Get the domain for lots in `move_line`."""
        move = move_line.move_id
        move_line_index = move.move_line_ids.ids.index(move_line.id)
        with tests.Form(
            move, view="stock.view_stock_move_operations"
        ) as move_form, move_form.move_line_ids.edit(move_line_index) as move_line_form:
            lot_field = move_line_form._view["tree"].xpath("//field[@name='lot_id']")[0]
            lot_domain_str = lot_field.get("domain")
            return safe_eval(
                lot_domain_str,
                globals_dict=move_line_form._proxy._records[0],
                nocopy=True,
            )

    def test_raw_filter_lot(self):
        """
        When "Use only available lots" is enabled
        in the production's picking type,
        the domain for the lot in raw move line
        only allows to select lots in the Components Location.
        """
        # Arrange
        production = self.production
        raw_location = production.location_src_id
        raw_location_lot = self.component_stock_lot
        no_raw_location_lot = self.component_other_stock_lot
        raw_move_line = production.move_raw_ids.move_line_ids
        # pre-condition
        self.assertTrue(production.picking_type_id.use_filter_lots)
        self.assertRecordValues(
            raw_move_line,
            [
                {
                    "picking_type_use_filter_lots": True,
                },
            ],
        )
        self.assertEqual(raw_location_lot.product_id, raw_move_line.product_id)
        self.assertEqual(raw_location_lot.quant_ids.location_id, raw_location)
        self.assertEqual(no_raw_location_lot.product_id, raw_move_line.product_id)
        self.assertNotEqual(no_raw_location_lot.quant_ids.location_id, raw_location)

        # Assert
        lot_domain = self._get_lots_domain(raw_move_line)
        available_lots = self.env["stock.production.lot"].search(lot_domain)
        self.assertIn(self.component_stock_lot, available_lots)
        self.assertNotIn(self.component_other_stock_lot, available_lots)

    def test_raw_no_filter_lot(self):
        """
        When "Use only available lots" is disabled
        in the production's picking type,
        the domain for the lot in raw move line
        allows to select any lot.
        """
        # Arrange
        production = self.production
        production.picking_type_id.use_filter_lots = False
        raw_location = production.location_src_id
        raw_location_lot = self.component_stock_lot
        no_raw_location_lot = self.component_other_stock_lot
        raw_move_line = production.move_raw_ids.move_line_ids
        # pre-condition
        self.assertFalse(production.picking_type_id.use_filter_lots)
        self.assertRecordValues(
            raw_move_line,
            [
                {
                    "picking_type_use_filter_lots": False,
                },
            ],
        )
        self.assertEqual(raw_location_lot.product_id, raw_move_line.product_id)
        self.assertEqual(raw_location_lot.quant_ids.location_id, raw_location)
        self.assertEqual(no_raw_location_lot.product_id, raw_move_line.product_id)
        self.assertNotEqual(no_raw_location_lot.quant_ids.location_id, raw_location)

        # Assert
        lot_domain = self._get_lots_domain(raw_move_line)
        available_lots = self.env["stock.production.lot"].search(lot_domain)
        self.assertIn(self.component_stock_lot, available_lots)
        self.assertIn(self.component_other_stock_lot, available_lots)
