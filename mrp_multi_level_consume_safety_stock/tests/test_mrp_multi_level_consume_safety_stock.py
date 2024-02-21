from datetime import datetime, timedelta

from odoo.addons.mrp_multi_level.tests.common import TestMrpMultiLevelCommon


class TestMrpMultiLevel(TestMrpMultiLevelCommon):
    def test_01_consume_safety_stock(self):
        now = datetime.now()
        self.cases_area.safety_stock_target_date = now.date() + timedelta(days=5)
        product = self.prod_test  # has Buy route
        product.seller_ids[0].delay = 2  # set a purchase lead time
        # current stock is 5
        self.quant_obj._update_available_quantity(product, self.cases_loc, 5)
        # safety stock is 15
        self.product_mrp_area_obj.create(
            {
                "product_id": product.id,
                "mrp_area_id": self.cases_area.id,
                "mrp_minimum_stock": 15,
                "mrp_applicable": True,  # needed?
            }
        )

        self._create_picking_out(
            product, 6.0, now + timedelta(days=3), location=self.cases_loc
        )
        self._create_picking_in(
            product, 10.0, now + timedelta(days=7), location=self.cases_loc
        )
        self._create_picking_out(
            product, 12.0, now + timedelta(days=14), location=self.cases_loc
        )
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.cases_area.ids)]}
        ).run_mrp_multi_level()
        inventory = self.mrp_inventory_obj.search(
            [
                ("mrp_area_id", "=", self.cases_area.id),
                ("product_id", "=", product.id),
            ]
        )
        expected = [
            {
                # only procure to get back to 0 while in the stress period
                "date": now.date() + timedelta(days=3),
                "demand_qty": 6.0,
                "final_on_hand_qty": -1.0,
                "initial_on_hand_qty": 5.0,
                "running_availability": -1.0,
                "supply_qty": 0.0,
                "to_procure": 0.0,
            },
            {
                # after stress period, rebuild safety stock
                "date": now.date() + timedelta(days=5),
                "demand_qty": 0.0,
                "final_on_hand_qty": -1.0,
                "initial_on_hand_qty": -1.0,
                "running_availability": 15.0,
                "supply_qty": 0.0,
                "to_procure": 16.0,
            },
            {
                "date": now.date() + timedelta(days=7),
                "demand_qty": 0.0,
                "final_on_hand_qty": 9.0,
                "initial_on_hand_qty": -1.0,
                "running_availability": 25.0,
                "supply_qty": 10.0,
                "to_procure": 0.0,
            },
            {
                "date": now.date() + timedelta(days=14),
                "demand_qty": 12.0,
                "final_on_hand_qty": -3.0,
                "initial_on_hand_qty": 9.0,
                "running_availability": 15.0,
                "supply_qty": 0.0,
                "to_procure": 2.0,
            },
        ]
        self.assertEqual(len(expected), len(inventory))
        for test_vals, inv in zip(expected, inventory):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date}",
                )
