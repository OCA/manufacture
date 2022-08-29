from odoo.tests import Form, common


class TestSubcontractedPickings(common.TransactionCase):
    def setUp(self):
        """
        - Create a vendor “Kitchen Supplies”
        - Create 3 different products of type 'consumable' supplied by "Kitchen Supplies":
            - "Fork": regular
            - "Spoon": regular
            - "Plate": subcontracted
        - Create a BOM for 'Plate'
        """
        super(TestSubcontractedPickings, self).setUp()

        # These variables are for convenience
        Product = self.env["product.product"]
        Partner = self.env["res.partner"]
        PurchaseOrder = self.env["purchase.order"]
        ProductSupplierInfo = self.env["product.supplierinfo"]
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseOrderLine = self.env["purchase.order.line"]

        # Create vendor
        self.vendor_id = Partner.create({"name": "Kitchen Supplies"})

        # Create Products and add supplier info for them
        self.product_fork_id = Product.create({"name": "Fork", "type": "consu"})
        ProductSupplierInfo.create(
            {
                "name": self.vendor_id.id,
                "product_tmpl_id": self.product_fork_id.product_tmpl_id.id,
            }
        )

        self.product_spoon_id = Product.create({"name": "Spoon", "type": "consu"})
        ProductSupplierInfo.create(
            {
                "name": self.vendor_id.id,
                "product_tmpl_id": self.product_spoon_id.product_tmpl_id.id,
            }
        )

        self.product_plate_id = Product.create({"name": "Plate", "type": "consu"})
        ProductSupplierInfo.create(
            {
                "name": self.vendor_id.id,
                "product_tmpl_id": self.product_plate_id.product_tmpl_id.id,
            }
        )
        # Create BOM for 'Plate'
        raw_material_id = Product.create({"name": "Raw Material"})
        self.bom_id = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_plate_id.product_tmpl_id.id,
                "type": "subcontract",
                "subcontractor_ids": [(4, self.vendor_id.id)],
                "bom_line_ids": [(0, 0, {"product_id": raw_material_id.id})],
            }
        )

        po_form = Form(PurchaseOrder)
        po_form.partner_id = self.vendor_id
        with po_form.order_line.new() as po_line:
            po_line.product_id = self.product_fork_id
            po_line.name = self.product_fork_id.name
        with po_form.order_line.new() as po_line:
            po_line.product_id = self.product_spoon_id
            po_line.name = self.product_spoon_id.name
        self.po_1_id = po_form.save()
        self.po_1_id.button_confirm()

        po_form = Form(PurchaseOrder)
        po_form.partner_id = self.vendor_id
        with po_form.order_line.new() as po_line:
            po_line.product_id = self.product_plate_id
            po_line.name = self.product_fork_id.name
        self.po_2_id = po_form.save()
        self.po_2_id.button_confirm()

        po_form = Form(PurchaseOrder)
        po_form.partner_id = self.vendor_id
        with po_form.order_line.new() as po_line:
            po_line.product_id = self.product_fork_id
            po_line.name = self.product_fork_id.name
        with po_form.order_line.new() as po_line:
            po_line.product_id = self.product_spoon_id
            po_line.name = self.product_spoon_id.name
        with po_form.order_line.new() as po_line:
            po_line.product_id = self.product_plate_id
            po_line.name = self.product_spoon_id.name
        self.po_3_id = po_form.save()
        self.po_3_id.button_confirm()

    def test_01_purchase_regular_products_only(self):
        """
        Preparation:
        - Create a new RFQ from “Kitchen Supplies”: 1xFork, 1xSpoon
        - Confirm RFQ

        Expected result:
        - One picking is created in state “Ready” for 1xFork and 1xFork
        """

        # Ensure PO is confirmed
        self.assertEqual(
            self.po_1_id.state,
            "purchase",
            msg="Purchase Order must be in state 'Purchase'",
        )

        # Ensure PO has a singe picking
        self.assertEqual(
            len(self.po_1_id.picking_ids),
            1,
            msg="Purchase Order must have a single picking",
        )

        # Ensure PO picking is in 'Ready' state
        picking = self.po_1_id.picking_ids[0]
        self.assertEqual(
            picking.state, "assigned", msg="Picking must be in 'Ready' state"
        )

        # Ensure PO picking contains correct products
        product_ids = (
            picking.move_ids_without_package.mapped("product_id").sorted("id").ids
        )
        self.assertEqual(
            [self.product_fork_id.id, self.product_spoon_id.id],
            product_ids,
            msg="'Fork' and 'Spoon' must be in the picking",
        )

    def test_02_purchase_subcontracted_product_only(self):
        """
        Preparation:
        - Create a new RFQ from “Kitchen Supplies”: 1xPlate
        - Confirm RFQ

        Expected result:
        - One picking is created: in state “Subcontracted” for 1xPlate
        """

        # Ensure PO is confirmed
        self.assertEqual(
            self.po_2_id.state,
            "purchase",
            msg="Purchase Order must be in state 'Purchase'",
        )

        # Ensure PO has a singe picking
        self.assertEqual(
            len(self.po_2_id.picking_ids),
            1,
            msg="Purchase Order must have a single picking",
        )

        # Ensure PO picking is in 'Subcontracted' state
        picking = self.po_2_id.picking_ids[0]
        self.assertEqual(
            picking.state, "subcontracted", msg="Picking must be in 'Ready' state"
        )

        # Ensure PO picking contains correct products
        product_ids = (
            picking.move_ids_without_package.mapped("product_id").sorted("id").ids
        )
        self.assertEqual(
            [self.product_plate_id.id],
            product_ids,
            msg="'Plate' must be in the picking",
        )

    def test_03_purchase_mixed_products(self):
        """
        Preparation:
        - Create a new RFQ from “Kitchen Supplies”: 1xFork, 1xSpoon, 1xPlate
        - Confirm RFQ

        Expected result:
        - Two pickings are created:
            1. In state “Ready” for 1xFork and 1xFork
            2. In state “Subcontracted” for 1xPlate
        """

        # Ensure PO is confirmed
        self.assertEqual(
            self.po_3_id.state,
            "purchase",
            msg="Purchase Order must be in state 'Purchase'",
        )

        # Ensure PO has two pickings
        self.assertEqual(
            len(self.po_3_id.picking_ids), 2, msg="Purchase Order must two pickings"
        )

        # Ensure PO pickings are in 'Ready' and 'Subcontracted' states
        pickings = self.po_3_id.picking_ids
        picking_states = set(pickings.mapped("state"))
        self.assertEqual(len(picking_states), 2, msg="Must be two picking states only")
        self.assertIn(
            "assigned", picking_states, msg="There must be a picking in 'Ready' state"
        )

        # Ensure PO pickings contains correct products
        # Regular products
        picking = pickings.filtered(lambda p: p.state == "assigned")
        product_ids = (
            picking.move_ids_without_package.mapped("product_id").sorted("id").ids
        )
        self.assertEqual(
            [
                self.product_fork_id.id,
                self.product_spoon_id.id,
            ],
            product_ids,
            msg="'Fork' and 'Spoon' must be in the picking",
        )

        # Subcontracted product
        picking = pickings.filtered(lambda p: p.state == "subcontracted")
        product_ids = (
            picking.move_ids_without_package.mapped("product_id").sorted("id").ids
        )
        self.assertEqual(
            self.product_plate_id.ids,
            product_ids,
            msg="Result must be equal to empty list",
        )
