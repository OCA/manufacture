# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpMtoWithStock(TransactionCase):
    def setUp(self):
        super().setUp()
        self.production_model = self.env["mrp.production"]
        self.procurement_model = self.env["procurement.group"]
        self.bom_model = self.env["mrp.bom"]
        self.stock_location_stock = self.env.ref("stock.stock_location_stock")
        self.manufacture_route = self.env.ref("mrp.route_warehouse0_manufacture")
        self.warehouse = self.env.ref("stock.warehouse0")

        self.top_product = self.env.ref(
            "mrp_mto_with_stock.product_product_manufacture_1"
        )
        self.subproduct1 = self.env.ref(
            "mrp_mto_with_stock.product_product_manufacture_1_1"
        )
        self.subproduct2 = self.env.ref(
            "mrp_mto_with_stock.product_product_manufacture_1_2"
        )
        self.subproduct_1_1 = self.env.ref(
            "mrp_mto_with_stock.product_product_manufacture_1_1_1"
        )

        self.main_bom = self.env.ref("mrp_mto_with_stock.mrp_bom_manuf_1")

    def _update_product_qty(self, product, quantity):
        """Update Product quantity."""
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "location_id": self.stock_location_stock.id,
                "inventory_quantity": quantity,
            }
        ).action_apply_inventory()

    def _create_production(self, qty):
        production = Form(self.env["mrp.production"])
        production.product_id = self.top_product
        production.bom_id = self.main_bom
        production.product_qty = qty
        return production.save()

    def _search_productions(self, product):
        return self.production_model.search([("product_id", "=", product.id)])

    def test_manufacture_with_forecast_stock(self):
        """
        Test Manufacture mto with stock based on forecast quantity
        and no link between sub assemblies MO's and Main MO raw material
        """
        self.warehouse.mrp_mto_mts_forecast_qty = True
        self._update_product_qty(self.subproduct1, 2)
        self._update_product_qty(self.subproduct2, 4)

        production = self._create_production(1.0)
        self.assertEqual(production.state, "draft")
        production.action_confirm()
        production.action_assign()
        # 5 units of Subproduct 1 are needed and only 2 are forecasted:
        # a procurement is created for the 3 missing ones.
        sub1_mo = self._search_productions(self.subproduct1)
        self.assertEqual(len(sub1_mo), 1)
        self.assertEqual(sub1_mo.product_qty, 3)
        # The forecast covers the 2 units of Subproduct 2.
        self.assertFalse(self._search_productions(self.subproduct2))
        # The procurement is not linked to the raw material move.
        raw_move = production.move_raw_ids.filtered(
            lambda m: m.product_id == self.subproduct1
        )
        self.assertFalse(raw_move.move_orig_ids)

        # The stock is now fully taken into account in the forecast, so a
        # second MO requires the whole quantity to be procured.
        production2 = self._create_production(1.0)
        production2.action_confirm()
        production2.action_assign()
        sub1_mo = self._search_productions(self.subproduct1)
        self.assertEqual(sum(sub1_mo.mapped("product_qty")), 8)
        production2.do_unreserve()

    def test_manufacture_with_reservable_stock(self):
        """
        Test Manufacture mto with stock based on reservable stock
        and there is a link between sub assemblies MO's and Main MO raw
        material
        """
        self._update_product_qty(self.subproduct1, 2)
        self._update_product_qty(self.subproduct2, 4)
        self._update_product_qty(self.subproduct_1_1, 50)
        self.main_bom.write(
            {
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.subproduct_1_1.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.subproduct_1_1.uom_id.id,
                        },
                    )
                ]
            }
        )
        production = self._create_production(3.0)
        self.assertEqual(len(production.move_raw_ids), 3)
        production.action_confirm()

        # The raw moves of the products configured as MTO/MTS are split: one
        # part is taken from the stock and the other one is procured.
        self.assertEqual(len(production.move_raw_ids), 5)
        for product, qty_stock, qty_procure in (
            (self.subproduct1, 2, 13),
            (self.subproduct2, 4, 2),
        ):
            moves = production.move_raw_ids.filtered_domain(
                [("product_id", "=", product.id)]
            )
            mts_move = moves.filtered(lambda m: m.procure_method == "make_to_stock")
            mto_move = moves.filtered(lambda m: m.procure_method == "make_to_order")
            self.assertEqual(mts_move.product_uom_qty, qty_stock)
            self.assertEqual(mto_move.product_uom_qty, qty_procure)
            # The procured part is linked to the sub assembly MO.
            sub_mo = self._search_productions(product)
            self.assertEqual(len(sub_mo), 1)
            self.assertEqual(sub_mo.product_qty, qty_procure)
            self.assertEqual(mto_move.move_orig_ids, sub_mo.move_finished_ids)
            self.assertFalse(mts_move.move_orig_ids)
        # Products that are not configured keep the standard behaviour.
        move = production.move_raw_ids.filtered(
            lambda m: m.product_id == self.subproduct_1_1
        )
        self.assertEqual(len(move), 1)
        self.assertEqual(move.state, "assigned")
