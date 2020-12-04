# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestRestrictLot(SavepointCase):
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
        lot = self.env["stock.production.lot"].create(
            {
                "name": "lot1",
                "product_id": self.panel_wood_prd.id,
                "company_id": self.warehouse.company_id.id,
            }
        )

        group = self.env["procurement.group"].create({"name": "My test delivery"})
        move = self.env["stock.move"].create(
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
        move._action_confirm()
        mo = move.move_orig_ids.production_id
        self.assertEqual(mo.lot_producing_id.id, lot.id)
        self.assertEqual(mo.name, lot.name)
