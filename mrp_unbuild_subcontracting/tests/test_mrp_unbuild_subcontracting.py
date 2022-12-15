from odoo.tests import Form, TransactionCase


class TestSubcontractingPurchaseFlows(TransactionCase):
    def setUp(self):
        super().setUp()

        self.subcontractor = self.env["res.partner"].create(
            {"name": "SuperSubcontractor"}
        )

        self.finished, self.compo = self.env["product.product"].create(
            [
                {
                    "name": "SuperProduct",
                    "type": "product",
                },
                {
                    "name": "Component",
                    "type": "consu",
                },
            ]
        )

        self.bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished.product_tmpl_id.id,
                "type": "subcontract",
                "subcontractor_ids": [(6, 0, self.subcontractor.ids)],
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.compo.id,
                            "product_qty": 1,
                        },
                    )
                ],
            }
        )

    def test_purchase_and_return(self):
        """
        The user buys 10 x a subcontracted product P. He receives the 10
        products and then does a return with 3 x P. The test ensures that
        the unbuild is created with the correct quantities and states
        """
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.subcontractor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.finished.name,
                            "product_id": self.finished.id,
                            "product_uom_qty": 10,
                            "product_uom": self.finished.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )
        po.button_confirm()

        mo = self.env["mrp.production"].search([("bom_id", "=", self.bom.id)])
        self.assertTrue(mo)

        receipt = po.picking_ids
        receipt.move_lines.quantity_done = 10
        receipt.button_validate()

        return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_id=receipt.id, active_model="stock.picking"
            )
        )
        with return_form.product_return_moves.edit(0) as line:
            line.quantity = 3
            line.to_refund = True
        return_wizard = return_form.save()
        return_id, _ = return_wizard._create_returns()

        return_picking = self.env["stock.picking"].browse(return_id)
        return_picking.move_lines.quantity_done = 3
        subcontractor_location = self.subcontractor.property_stock_subcontractor
        unbuild = self.env["mrp.unbuild"].search([("bom_id", "=", self.bom.id)])

        self.assertTrue(unbuild)
        self.assertEqual(
            unbuild.state, "draft", "The state of the unbuild should be draft"
        )
        self.assertEqual(
            unbuild.product_qty, 3, "The quantity of the unbuild should be 3"
        )
        self.assertEqual(
            unbuild.location_id,
            subcontractor_location,
            "The source location of the unbuild should be the property stock "
            "of the subcontractor",
        )
        self.assertEqual(
            unbuild.location_dest_id,
            subcontractor_location,
            "The destination location of the unbuild should be the property "
            "stock of the subcontractor",
        )

        return_picking.button_validate()

        self.assertEqual(self.finished.qty_available, 7.0)
        self.assertEqual(po.order_line.qty_received, 7.0)
        self.assertEqual(
            unbuild.state, "done", "The state of the unbuild should be done"
        )

        move = return_picking.move_lines
        self.assertEqual(
            move.location_id,
            receipt.location_dest_id,
            "The source location of the stock move should be the same as "
            "destination location of the original purchase",
        )
        self.assertEqual(
            move.location_dest_id,
            subcontractor_location,
            "The destination location of the stock move should be the property "
            "stock of the subcontractor",
        )

        # Call the action to view the layers associated to the pickings
        result1 = return_picking.action_view_stock_valuation_layers()
        result2 = receipt.action_view_stock_valuation_layers()
        layers1 = result1["domain"][2][2]
        layers2 = result2["domain"][2][2]
        self.assertTrue(
            layers1,
        )
        self.assertTrue(
            layers2,
        )


class TestSubcontractingTracking(TransactionCase):
    def setUp(self):
        super(TestSubcontractingTracking, self).setUp()
        # 1: Create a subcontracting partner
        main_company_1 = self.env["res.partner"].create({"name": "main_partner"})
        self.subcontractor_partner1 = self.env["res.partner"].create(
            {
                "name": "Subcontractor 1",
                "parent_id": main_company_1.id,
                "company_id": self.env.ref("base.main_company").id,
            }
        )

        # 2. Create a BOM of subcontracting type
        # 2.1. Comp1 has tracking by lot
        self.comp1_sn = self.env["product.product"].create(
            {
                "name": "Component1",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
                "tracking": "serial",
            }
        )
        self.comp2 = self.env["product.product"].create(
            {
                "name": "Component2",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )

        # 2.2. Finished prodcut has tracking by serial number
        self.finished_product = self.env["product.product"].create(
            {
                "name": "finished",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
                "tracking": "lot",
            }
        )
        bom_form = Form(self.env["mrp.bom"])
        bom_form.type = "subcontract"
        bom_form.subcontractor_ids.add(self.subcontractor_partner1)
        bom_form.product_tmpl_id = self.finished_product.product_tmpl_id
        with bom_form.bom_line_ids.new() as bom_line:
            bom_line.product_id = self.comp1_sn
            bom_line.product_qty = 1
        with bom_form.bom_line_ids.new() as bom_line:
            bom_line.product_id = self.comp2
            bom_line.product_qty = 1
        self.bom_tracked = bom_form.save()

    def test_purchase_and_return_with_serial_numbers(self):
        """
        The user buys one subcontracted product P with serial number.
        Then does the return . The test ensures that the unbuild is
        created with the correct quantities, serial number of the product and states
        """
        # Create a receipt picking from the subcontractor
        picking_form = Form(self.env["stock.picking"])
        picking_form.picking_type_id = self.env.ref("stock.picking_type_in")
        picking_form.partner_id = self.subcontractor_partner1
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.finished_product
            move.product_uom_qty = 1
        picking_receipt = picking_form.save()
        picking_receipt.action_confirm()

        # We should be able to call the 'record_components' button
        self.assertTrue(picking_receipt.display_action_record_components)

        # Check the created manufacturing order
        mo = self.env["mrp.production"].search([("bom_id", "=", self.bom_tracked.id)])
        self.assertEqual(len(mo), 1)
        self.assertEqual(len(mo.picking_ids), 0)
        wh = picking_receipt.picking_type_id.warehouse_id
        self.assertEqual(mo.picking_type_id, wh.subcontracting_type_id)
        self.assertFalse(mo.picking_type_id.active)

        # Create a RR
        pg1 = self.env["procurement.group"].create({})
        self.env["stock.warehouse.orderpoint"].create(
            {
                "name": "xxx",
                "product_id": self.comp1_sn.id,
                "product_min_qty": 0,
                "product_max_qty": 0,
                "location_id": self.env.user.company_id.subcontracting_location_id.id,
                "group_id": pg1.id,
            }
        )

        # Run the scheduler and check the created picking
        self.env["procurement.group"].run_scheduler()
        picking = self.env["stock.picking"].search([("group_id", "=", pg1.id)])
        self.assertEqual(len(picking), 1)
        self.assertEqual(picking.picking_type_id, wh.out_type_id)

        lot_id = self.env["stock.production.lot"].create(
            {
                "name": "lot1",
                "product_id": self.finished_product.id,
                "company_id": self.env.company.id,
            }
        )
        serial_id = self.env["stock.production.lot"].create(
            {
                "name": "lot1",
                "product_id": self.comp1_sn.id,
                "company_id": self.env.company.id,
            }
        )

        action = picking_receipt.action_record_components()
        mo = self.env["mrp.production"].browse(action["res_id"])
        mo_form = Form(mo.with_context(**action["context"]), view=action["view_id"])
        mo_form.qty_producing = 1
        mo_form.lot_producing_id = lot_id
        with mo_form.move_line_raw_ids.edit(0) as ml:
            ml.lot_id = serial_id
        mo = mo_form.save()
        mo.subcontracting_record_component()

        # We should not be able to call the 'record_components' button
        self.assertFalse(picking_receipt.display_action_record_components)

        picking_receipt.button_validate()
        self.assertEqual(mo.state, "done")

        return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_id=picking_receipt.id, active_model="stock.picking"
            )
        )
        with return_form.product_return_moves.edit(0) as line:
            line.quantity = 1
            line.to_refund = True
        return_wizard = return_form.save()
        return_id, _ = return_wizard._create_returns()

        return_picking = self.env["stock.picking"].browse(return_id)
        return_picking.move_lines.quantity_done = 1
        subcontractor_location = (
            self.subcontractor_partner1.property_stock_subcontractor
        )
        unbuild = self.env["mrp.unbuild"].search([("bom_id", "=", self.bom_tracked.id)])

        self.assertTrue(unbuild)
        self.assertEqual(
            unbuild.state, "draft", "The state of the unbuild should be draft"
        )
        self.assertEqual(
            unbuild.product_qty, 1, "The quantity of the unbuild should be 1"
        )
        self.assertEqual(
            unbuild.location_id,
            subcontractor_location,
            "The source location of the unbuild should be the property stock "
            "of the subcontractor",
        )
        self.assertEqual(
            unbuild.location_dest_id,
            subcontractor_location,
            "The destination location of the unbuild should be the property "
            "stock of the subcontractor",
        )
        return_picking.move_line_ids_without_package.lot_id = lot_id
        return_picking.button_validate()

        self.assertEqual(
            unbuild.state, "done", "The state of the unbuild should be done"
        )

        move = return_picking.move_lines
        self.assertEqual(
            move.location_id,
            picking_receipt.location_dest_id,
            "The source location of the stock move should be the same as "
            "destination location of the original purchase",
        )
        self.assertEqual(
            move.location_dest_id,
            subcontractor_location,
            "The destination location of the stock move should be the property "
            "stock of the subcontractor",
        )
