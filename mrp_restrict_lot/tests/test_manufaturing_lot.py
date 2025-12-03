# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestRestrictLot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.panel_wood_prd = cls.env.ref("mrp.product_product_wood_panel")
        manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        mto_route = cls.env.ref("stock.route_warehouse0_mto")
        mto_route.write({"active": True})
        # ensure full make to order and not mts or mto
        mto_route.rule_ids.write({"procure_method": "make_to_order"})
        cls.panel_wood_prd.write(
            {"route_ids": [(4, manufacture_route.id, 0), (4, mto_route.id, 0)]}
        )
        cls.out_picking_type = cls.env.ref("stock.picking_type_out")

    def test_manufacturing_lot(self):
        lot = self.env["stock.lot"].create(
            {
                "name": "lot1",
                "product_id": self.panel_wood_prd.id,
                "company_id": self.warehouse.company_id.id,
            }
        )
        lot2 = self.env["stock.lot"].create(
            {
                "name": "lot2",
                "product_id": self.panel_wood_prd.id,
                "company_id": self.warehouse.company_id.id,
            }
        )

        group = self.env["procurement.group"].create({"name": "My test delivery"})
        move1 = self.env["stock.move"].create(
            {
                "product_id": self.panel_wood_prd.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.customer_loc.id,
                "product_uom_qty": 1,
                "product_uom": self.panel_wood_prd.uom_id.id,
                "name": "test",
                "procure_method": "make_to_order",
                "warehouse_id": self.warehouse.id,
                "restrict_lot_id": lot.id,
                "picking_type_id": self.out_picking_type.id,
                "group_id": group.id,
            }
        )
        move1._action_confirm()
        mo1 = move1.move_orig_ids.production_id
        self.assertEqual(mo1.lot_producing_id.id, lot.id)
        self.assertEqual(mo1.name, lot.name)
        group2 = self.env["procurement.group"].create({"name": "My test delivery 2"})
        move2 = self.env["stock.move"].create(
            {
                "product_id": self.panel_wood_prd.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.customer_loc.id,
                "product_uom_qty": 1,
                "product_uom": self.panel_wood_prd.uom_id.id,
                "name": "test",
                "procure_method": "make_to_order",
                "warehouse_id": self.warehouse.id,
                "restrict_lot_id": lot.id,
                "picking_type_id": self.out_picking_type.id,
                "group_id": group2.id,
            }
        )
        move2._action_confirm()
        mo2 = move2.move_orig_ids.production_id
        self.assertEqual(mo2.name, f"{lot.name}-1")
        self.assertEqual(
            mo2.move_finished_ids.restrict_lot_id,
            lot,
            "ensure propagation of the restricted lot to the finished move",
        )

        mo2.button_mark_done()
        self.assertEqual(mo2.state, "done")
        self.assertEqual(mo2.lot_producing_id.id, lot.id)
        self.assertEqual(
            mo2.move_finished_ids.restrict_lot_id,
            lot,
            "ensure propagation of the restricted lot to the finished move after prod",
        )

        # change lot on MO 1 and ensure it's propagated
        mo1.lot_producing_id = lot2
        mo1.button_mark_done()
        self.assertEqual(mo1.state, "done")
        self.assertEqual(
            mo1.lot_producing_id.id,
            lot2.id,
            "lot_producing_id should propagate to move line",
        )
        self.assertEqual(
            mo1.move_finished_ids.restrict_lot_id,
            lot2,
            "ensure propagation of the restricted lot to the finished move after prod",
        )
