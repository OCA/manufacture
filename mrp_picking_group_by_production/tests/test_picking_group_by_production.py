# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase


class TestPickingGroupByProduction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "Test Warehouse", "code": "TWH", "manufacture_steps": "pbm_sam"}
        )
        cls.component = cls.env["product.product"].create(
            {"name": "Component", "type": "consu", "is_storable": True}
        )
        cls.finished = cls.env["product.product"].create(
            {"name": "Finished", "type": "consu", "is_storable": True}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.component, cls.warehouse.lot_stock_id, 100
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished.product_tmpl_id.id,
                "product_qty": 1,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.component.id, "product_qty": 1})
                ],
            }
        )
        cls.reference = cls.env["stock.reference"].create({"name": "SO/TEST"})

    def _create_production(self, qty):
        production = self.env["mrp.production"].create(
            {
                "product_id": self.finished.id,
                "product_qty": qty,
                "bom_id": self.bom.id,
                "picking_type_id": self.warehouse.manu_type_id.id,
                "reference_ids": [(6, 0, self.reference.ids)],
            }
        )
        production.action_confirm()
        return production

    def _pick_components(self, production):
        return production.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse.pbm_type_id
        )

    def test_one_pick_components_per_production(self):
        """Two orders sharing a reference get their own pick components."""
        production_1 = self._create_production(5)
        production_2 = self._create_production(7)
        pick_1 = self._pick_components(production_1)
        pick_2 = self._pick_components(production_2)
        self.assertEqual(len(pick_1), 1)
        self.assertEqual(len(pick_2), 1)
        self.assertNotEqual(pick_1, pick_2)
        self.assertEqual(
            pick_1.move_ids.production_group_id, production_1.production_group_id
        )
        self.assertEqual(
            pick_2.move_ids.production_group_id, production_2.production_group_id
        )
        self.assertEqual(sum(pick_1.move_ids.mapped("product_uom_qty")), 5)
        self.assertEqual(sum(pick_2.move_ids.mapped("product_uom_qty")), 7)

    def test_moves_without_production_still_grouped(self):
        """Moves that do not come from a production keep the standard grouping."""
        moves = self.env["stock.move"].create(
            [
                {
                    "product_id": self.component.id,
                    "product_uom_qty": qty,
                    "product_uom": self.component.uom_id.id,
                    "location_id": self.warehouse.lot_stock_id.id,
                    "location_dest_id": self.warehouse.lot_stock_id.id,
                    "picking_type_id": self.warehouse.int_type_id.id,
                    "reference_ids": [(6, 0, self.reference.ids)],
                }
                for qty in (1, 2)
            ]
        )
        self.assertFalse(moves[0]._group_picking_by_production())
        moves._action_confirm()
        # the two moves are merged into a single transfer, as in standard Odoo
        moves = moves.exists()
        self.assertEqual(len(moves), 1)
        self.assertEqual(len(moves.picking_id), 1)
        self.assertEqual(moves.product_uom_qty, 3)
