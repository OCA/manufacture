# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.mrp_lot_number_propagation.tests.common import Common


class TestMrpSubcontracting(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sub_lot_name = "SUBCONTRACT-SN-001"
        cls.vendor = cls.env["res.partner"].create(
            {"name": "Subcontractor Vendor (test)"}
        )
        cls.component = cls.env["product.product"].create(
            {
                "name": "Subcontract component serial (test)",
                "is_storable": True,
                "tracking": "serial",
            }
        )
        cls.component_lot = cls.env["stock.lot"].create(
            {
                "name": cls.sub_lot_name,
                "product_id": cls.component.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.finished_product = cls.env["product.product"].create(
            {
                "name": "Subcontracted finished product (test)",
                "is_storable": True,
                "tracking": "serial",
            }
        )
        cls.subcontracted_bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished_product.product_tmpl_id.id,
                "product_qty": 1,
                "type": "subcontract",
                "subcontractor_ids": [(6, 0, cls.vendor.ids)],
                "lot_number_propagation": True,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.component.id,
                            "product_qty": 1,
                            "propagate_lot_number": True,
                        },
                    )
                ],
            }
        )
        warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        # The component is available at the subcontractor's location
        cls._update_qty_in_location(
            warehouse.lot_stock_id, cls.component, 1, lot=cls.component_lot
        )
        picking_type = warehouse.in_type_id
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "partner_id": cls.vendor.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.finished_product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.finished_product.uom_id.id,
                            "location_id": picking_type.default_location_src_id.id,
                            "location_dest_id": (
                                picking_type.default_location_dest_id.id
                            ),
                        },
                    )
                ],
            }
        )
        cls.picking.action_confirm()

    def _set_qty_done(self, order):
        for line in order.move_raw_ids.move_line_ids:
            line.quantity = line.quantity_product_uom
            line.picked = True
        order.qty_producing = order.product_qty

    def test_lot_propagation(self):
        order = self.picking.move_ids.move_orig_ids.production_id
        self.assertEqual(order.bom_id, self.subcontracted_bom)
        self.assertFalse(order.propagated_lot_producing)
        # Resupply the subcontractor: stock -> subcontracting location
        resupply = order.move_raw_ids.move_orig_ids.picking_id
        self.assertTrue(resupply)
        resupply.action_assign()
        self.assertEqual(resupply.state, "assigned")
        resupply.move_ids.picked = True
        resupply.with_context(skip_backorder=True, skip_sms=True).button_validate()
        self.assertEqual(resupply.state, "done")
        # The component is now reserved with its serial: the expected serial
        # of the finished product is known, but nothing is assigned yet
        self.assertTrue(order.move_raw_ids.move_line_ids)
        self.assertEqual(order.propagated_lot_producing, self.sub_lot_name)
        self.assertFalse(order.lot_producing_ids)
        self.assertFalse(self.picking.move_line_ids.lot_id)
        dest_location = self.picking.move_ids.location_dest_id
        # Validating the receipt propagates the serial and closes the MO
        self.picking.move_ids.picked = True
        self.picking.with_context(skip_backorder=True).button_validate()
        self.assertEqual(self.picking.state, "done")
        subcontract_move = self.picking.move_ids.filtered(lambda m: m.is_subcontract)
        production = subcontract_move.move_orig_ids.production_id
        self.assertTrue(production)
        self.assertEqual(production.state, "done")
        self.assertEqual(production.lot_producing_ids.name, self.sub_lot_name)
        # The serial is on the receipt and the finished product is in stock
        lot = self.picking.move_line_ids.lot_id
        self.assertEqual(lot.name, self.sub_lot_name)
        quant = self.env["stock.quant"].search(
            [
                ("lot_id", "=", lot.id),
                ("location_id", "=", dest_location.id),
            ]
        )

        self.assertTrue(quant)
        self.assertEqual(sum(quant.mapped("quantity")), 1.0)
        # The component serial has been consumed
        self.assertEqual(
            production.move_raw_ids.move_line_ids.lot_id, self.component_lot
        )
        self.assertTrue(production.move_raw_ids.picked)
