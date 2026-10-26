from odoo.tests.common import TransactionCase


class TestQCCheckWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wiz_model = cls.env["qc.check.wizard"]

        cls.test_location = cls.env.ref("stock.stock_location_stock")
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )
        cls.picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Test Operation Type",
                "sequence_code": "1",
                "code": "incoming",
            }
        )

        cls.stock_picking1 = cls.env["stock.picking"].create(
            {
                "location_id": cls.test_location.id,
                "location_dest_id": cls.test_location.id,
                "picking_type_id": cls.picking_type.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": 1,
                            "product_uom_qty": 1,
                            "product_uom": 1,
                            "name": "Test Product",
                            "location_id": cls.test_location.id,
                            "location_dest_id": cls.test_location.id,
                        },
                    )
                ],
            }
        )

    def test_qc_check_wizard(self):
        wizard = self.wiz_model.create({"stock_picking_ids": self.stock_picking1.ids})
        self.assertTrue(wizard.stock_picking_ids)

        move1 = self.stock_picking1.move_ids[0]
        move1.quantity_done = 1

        wizard.action_complete_inspections()
        self.assertNotEqual(self.stock_picking1.state, "done")

        wizard.action_skip_inspections()
        self.assertEqual(self.stock_picking1.state, "done")
