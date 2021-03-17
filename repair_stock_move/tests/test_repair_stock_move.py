# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo.tests import common


class TestRepairStockMove(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestRepairStockMove, cls).setUpClass()
        # Partners
        cls.res_partner_1 = cls.env["res.partner"].create({"name": "Wood Corner"})
        cls.res_partner_address_1 = cls.env["res.partner"].create(
            {"name": "Willie Burke", "parent_id": cls.res_partner_1.id}
        )
        cls.res_partner_12 = cls.env["res.partner"].create({"name": "Partner 12"})

        # Products
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Desk Combination", "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Conference Chair", "type": "product"}
        )
        cls.product_3 = cls.env["product.product"].create(
            {"name": "Large Cabinet", "type": "product"}
        )
        cls.service = cls.env["product.product"].create(
            {
                "name": "Repair Services",
                "type": "service",
            }
        )

        # Location
        cls.stock_warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock_location_14 = cls.env["stock.location"].create(
            {
                "name": "Shelf 2",
                "location_id": cls.stock_warehouse.lot_stock_id.id,
            }
        )

        # Replenish products
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, cls.stock_location_14, 1
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_2, cls.stock_location_14, 1
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_3, cls.stock_location_14, 1
        )

        # Repair Orders
        dest_loc_id = cls.product_1.property_stock_production.id
        cls.repair1 = cls.env["repair.order"].create(
            {
                "address_id": cls.res_partner_address_1.id,
                "guarantee_limit": "2019-01-01",
                "invoice_method": "none",
                "user_id": False,
                "product_id": cls.product_1.id,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "partner_invoice_id": cls.res_partner_address_1.id,
                "location_id": cls.stock_location_14.id,
                "operations": [
                    (
                        0,
                        0,
                        {
                            "location_dest_id": dest_loc_id,
                            "location_id": cls.stock_location_14.id,
                            "name": cls.product_1.display_name,
                            "product_id": cls.product_2.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1.0,
                            "price_unit": 50.0,
                            "state": "draft",
                            "type": "add",
                            "company_id": cls.env.company.id,
                        },
                    )
                ],
                "fees_lines": [
                    (
                        0,
                        0,
                        {
                            "name": cls.service.display_name,
                            "product_id": cls.service.id,
                            "product_uom_qty": 1.0,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "price_unit": 50.0,
                            "company_id": cls.env.company.id,
                        },
                    )
                ],
                "partner_id": cls.res_partner_12.id,
            }
        )

        cls.env.user.groups_id |= cls.env.ref("stock.group_stock_user")

    def test_stock_move_state(self):
        # Validate Repair Order
        self.repair1.action_validate()
        self.assertEqual(
            self.repair1.move_id.state,
            "confirmed",
            "Generated stock move state should be confirmed",
        )
        for operation in self.repair1.operations:
            self.assertEqual(
                operation.move_id.state,
                "confirmed",
                "Generated stock move state should be confirmed",
            )
        # Start Repair
        self.repair1.action_repair_start()
        # End Repair
        self.repair1.action_repair_end()
        self.assertEqual(
            self.repair1.move_id.state,
            "done",
            "Generated stock move state should be done",
        )
        for operation in self.repair1.operations:
            self.assertEqual(
                operation.move_id.state,
                "done",
                "Generated stock move state should be done",
            )

    def _create_simple_repair_order(self, invoice_method):
        product_to_repair = self.product_1
        partner = self.res_partner_address_1
        return self.env["repair.order"].create(
            {
                "product_id": product_to_repair.id,
                "product_uom": product_to_repair.uom_id.id,
                "address_id": partner.id,
                "guarantee_limit": "2019-01-01",
                "invoice_method": invoice_method,
                "partner_invoice_id": partner.id,
                "location_id": self.stock_location_14.id,
                "partner_id": self.res_partner_12.id,
            }
        )

    def _create_simple_operation(self, repair_id=False, qty=0.0, price_unit=0.0):
        product_to_add = self.product_1
        return self.env["repair.line"].create(
            {
                "name": "Add The product",
                "type": "add",
                "product_id": product_to_add.id,
                "product_uom_qty": qty,
                "product_uom": product_to_add.uom_id.id,
                "price_unit": price_unit,
                "repair_id": repair_id,
                "location_id": self.stock_location_14.id,
                "location_dest_id": product_to_add.property_stock_production.id,
                "company_id": self.env.company.id,
            }
        )

    # def _create_simple_fee(self, repair_id=False, qty=0.0, price_unit=0.0):
    #     service = self.product_1
    #     return self.env['repair.fee'].create({
    #         'name': 'PC Assemble + Custom (PC on Demand)',
    #         'product_id': service.id,
    #         'product_uom_qty': qty,
    #         'product_uom': service.uom_id.id,
    #         'price_unit': price_unit,
    #         'repair_id': repair_id,
    #         'company_id': self.env.company.id,
    #     })
