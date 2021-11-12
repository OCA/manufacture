# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo.tests.common import TransactionCase


class TestRepairType(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestRepairType, self).setUp(*args, **kwargs)

        # First of all we create a repair to work with
        self.repair_r1 = self.env.ref("repair.repair_r1")

        # Now we will create a location scrap for the destination location of removed components
        stock_location_locations_virtual = self.env["stock.location"].create(
            {"name": "Virtual Locations", "usage": "view", "posz": 1}
        )
        self.scrapped_location = self.env["stock.location"].create(
            {
                "name": "Scrapped",
                "location_id": stock_location_locations_virtual.id,
                "scrap_location": True,
                "usage": "inventory",
            }
        )

        # Then, we create a repair type to know the source and destination locations
        self.repair_type_1 = self.env["repair.type"].create(
            {
                "name": "Repairings Office 1",
                "source_location_id": self.env.ref("stock.stock_location_stock").id,
                "destination_location_id": self.env.ref(
                    "stock.stock_location_customers"
                ).id,
                "source_location_add_part_id": self.env.ref(
                    "stock.stock_location_components"
                ).id,
                "destination_location_add_part_id": self.env.ref(
                    "stock.stock_location_customers"
                ).id,
                "source_location_remove_part_id": self.env.ref(
                    "stock.stock_location_stock"
                ).id,
                "destination_location_remove_part_id": self.scrapped_location.id,
            }
        )
        self.repair_type_2 = self.env["repair.type"].create(
            {
                "name": "Repairings Office 2",
                "source_location_id": self.env.ref(
                    "stock.stock_location_components"
                ).id,
                "destination_location_id": self.env.ref(
                    "stock.stock_location_stock"
                ).id,
                "source_location_add_part_id": self.env.ref(
                    "stock.location_refrigerator_small"
                ).id,
                "destination_location_add_part_id": self.env.ref(
                    "stock.stock_location_14"
                ).id,
                "source_location_remove_part_id": self.env.ref(
                    "stock.stock_location_stock"
                ).id,
                "destination_location_remove_part_id": self.scrapped_location.id,
            }
        )

        # Finally we add two line components to the repair order,
        # one adding a component and the other one removing
        self.add_component = self.env["repair.line"].create(
            {
                "name": "Add Component 1",
                "repair_id": 1,
                "price_unit": 2.0,
                "type": "add",
                "product_id": self.env.ref("product.product_product_3").id,
                "product_uom": self.env.ref("product.product_product_3").uom_id.id,
                "product_uom_qty": 1.0,
                "location_id": self.env.ref("stock.stock_location_14").id,
                "location_dest_id": self.env.ref(
                    "product.product_product_3"
                ).property_stock_production.id,
                "company_id": self.env.company.id,
            }
        )
        self.remove_component = self.env["repair.line"].create(
            {
                "name": "Add Component 2",
                "repair_id": 1,
                "price_unit": 2.0,
                "type": "remove",
                "product_id": self.env.ref("product.product_product_11").id,
                "product_uom": self.env.ref("product.product_product_11").uom_id.id,
                "product_uom_qty": 1.0,
                "location_id": self.env.ref("stock.stock_location_14").id,
                "location_dest_id": self.env.ref(
                    "product.product_product_11"
                ).property_stock_production.id,
                "company_id": self.env.company.id,
            }
        )
        self.repair_r1.operations |= self.add_component
        self.repair_r1.operations |= self.remove_component

    def test_compute_location_id(self):
        # First we associate the repair with the repair type
        self.repair_r1.repair_type_id = self.repair_type_1

        # Afterwards we will assert the source and
        # destination of the product in the repair order
        self.assertEqual(
            self.repair_r1.location_id, self.repair_type_1.source_location_id
        )

        # Next we assert if the source and destination locations of the components are correct
        self.assertEqual(
            self.repair_r1.operations[0].location_id,
            self.repair_type_1.source_location_add_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[0].location_dest_id,
            self.repair_type_1.destination_location_add_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[1].location_id,
            self.repair_type_1.source_location_add_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[1].location_dest_id,
            self.repair_type_1.destination_location_add_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[2].location_id,
            self.repair_type_1.source_location_remove_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[2].location_dest_id,
            self.repair_type_1.destination_location_remove_part_id,
        )

        # We change the repair type to repair_type_2 and check if all the locations changed
        self.repair_r1.repair_type_id = self.repair_type_2

        self.assertEqual(
            self.repair_r1.location_id, self.repair_type_2.source_location_id
        )

        self.assertEqual(
            self.repair_r1.operations[0].location_id,
            self.repair_type_2.source_location_add_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[0].location_dest_id,
            self.repair_type_2.destination_location_add_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[1].location_id,
            self.repair_type_2.source_location_add_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[1].location_dest_id,
            self.repair_type_2.destination_location_add_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[2].location_id,
            self.repair_type_2.source_location_remove_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[2].location_dest_id,
            self.repair_type_2.destination_location_remove_part_id,
        )

    def test_compute_location_id_2(self):
        # First we will assert the source and destination
        # of the component product in the repair order
        self.repair_r1.repair_type_id = self.repair_type_1

        self.assertEqual(
            self.repair_r1.operations[0].location_id,
            self.repair_type_1.source_location_add_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[0].location_dest_id,
            self.repair_type_1.destination_location_add_part_id,
        )

        # Then we change the type of operation
        self.repair_r1.operations[0].type = "remove"

        # And finally we assert that the locations of that operation changed
        self.assertEqual(
            self.repair_r1.operations[0].location_id,
            self.repair_type_1.source_location_remove_part_id,
        )
        self.assertEqual(
            self.repair_r1.operations[0].location_dest_id,
            self.repair_type_1.destination_location_remove_part_id,
        )
