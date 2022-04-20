from odoo.tests import common


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
        self.Product = self.env["product.product"]
        self.ProductSupplierInfo = self.env["product.supplierinfo"]
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseOrderLine = self.env["purchase.order.line"]

        # Create vendor
        self.vendor_id = self.env["res.partner"].create({"name": "Kitchen Supplies"})

        # Create Products and add supplier info for them
        self.product_fork_id = self.Product.create({"name": "Fork", "type": "consu"})
        self.ProductSupplierInfo.create(
            {
                "name": self.vendor_id.id,
                "product_tmpl_id": self.product_fork_id.product_tmpl_id.id,
            }
        )

        self.product_spoon_id = self.Product.create({"name": "Spoon", "type": "consu"})
        self.ProductSupplierInfo.create(
            {
                "name": self.vendor_id.id,
                "product_tmpl_id": self.product_spoon_id.product_tmpl_id.id,
            }
        )

        self.product_plate_id = self.Product.create({"name": "Plate", "type": "consu"})
        self.ProductSupplierInfo.create(
            {
                "name": self.vendor_id.id,
                "product_tmpl_id": self.product_plate_id.product_tmpl_id.id,
            }
        )
        # Create BOM for 'Plate'
        raw_material_id = self.Product.create({"name": "Raw Material"})
        self.bom_id = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_plate_id.product_tmpl_id.id,
                "type": "subcontract",
                "subcontractor_ids": [(4, self.vendor_id.id)],
                "bom_line_ids": [(0, 0, {"product_id": raw_material_id.id})],
            }
        )

    def test_01_purchase_regular_products_only(self):
        """
        Preparation:
        - Create a new RFQ from “Kitchen Supplies”: 1xFork, 1xSpoon
        - Confirm RFQ

        Expected result:
        - One picking is created in state “Ready” for 1xFork and 1xFork
        """

        # Create a new PO
        po_id = self.PurchaseOrder.create(
            {
                "partner_id": self.vendor_id.id,
            }
        )

        # Create PO Lines
        po_line_vals = [
            {
                "order_id": po_id.id,
                "product_id": self.product_fork_id.id,
                "name": self.product_fork_id.name,
            },
            {
                "order_id": po_id.id,
                "product_id": self.product_spoon_id.id,
                "name": self.product_spoon_id.name,
            },
        ]
        self.PurchaseOrderLine.create(po_line_vals)

        # Confirm the PO
        po_id.button_confirm()

        # Ensure PO is confirmed
        self.assertEqual(
            po_id.state, "purchase", msg="Purchase Order must be in state 'Purchase'"
        )

        # Ensure PO has a singe picking
        self.assertEqual(
            len(po_id.picking_ids), 1, msg="Purchase Order must have a single picking"
        )

        # Ensure PO picking is in 'Ready' state
        picking = po_id.picking_ids[0]
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

        # Create a new PO
        po_id = self.PurchaseOrder.create(
            {
                "partner_id": self.vendor_id.id,
            }
        )

        # Create PO Lines
        po_line_vals = [
            {
                "order_id": po_id.id,
                "product_id": self.product_plate_id.id,
                "name": self.product_fork_id.name,
            },
        ]
        self.PurchaseOrderLine.create(po_line_vals)

        # Confirm the PO
        po_id.button_confirm()

        # Ensure PO is confirmed
        self.assertEqual(
            po_id.state, "purchase", msg="Purchase Order must be in state 'Purchase'"
        )

        # Ensure PO has a singe picking
        self.assertEqual(
            len(po_id.picking_ids), 1, msg="Purchase Order must have a single picking"
        )

        # Ensure PO picking is in 'Subcontracted' state
        picking = po_id.picking_ids[0]
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

        # Create a new PO
        po_id = self.PurchaseOrder.create(
            {
                "partner_id": self.vendor_id.id,
            }
        )

        # Create PO Lines
        po_line_vals = [
            {
                "order_id": po_id.id,
                "product_id": self.product_fork_id.id,
                "name": self.product_fork_id.name,
            },
            {
                "order_id": po_id.id,
                "product_id": self.product_spoon_id.id,
                "name": self.product_spoon_id.name,
            },
            {
                "order_id": po_id.id,
                "product_id": self.product_plate_id.id,
                "name": self.product_spoon_id.name,
            },
        ]
        self.PurchaseOrderLine.create(po_line_vals)

        # Confirm the PO
        po_id.button_confirm()

        # Ensure PO is confirmed
        self.assertEqual(
            po_id.state, "purchase", msg="Purchase Order must be in state 'Purchase'"
        )

        # Ensure PO has two pickings
        self.assertEqual(
            len(po_id.picking_ids), 2, msg="Purchase Order must two pickings"
        )

        # Ensure PO pickings are in 'Ready' and 'Subcontracted' states
        pickings = po_id.picking_ids
        picking_states = pickings.mapped("state")
        self.assertEqual(len(picking_states), 2, msg="Must be two picking states only")
        self.assertIn(
            "assigned", picking_states, msg="There must be a picking in 'Ready' state"
        )
        self.assertIn(
            "subcontracted",
            picking_states,
            msg="There must be a picking in 'Subcontracted' state",
        )

        # Ensure PO pickings contains correct products
        # Regular products
        picking = pickings.filtered(lambda p: p.state == "assigned")
        product_ids = (
            picking.move_ids_without_package.mapped("product_id").sorted("id").ids
        )
        self.assertEqual(
            [self.product_fork_id.id, self.product_spoon_id.id],
            product_ids,
            msg="'Fork' and 'Spoon' must be in the picking",
        )

        # Subcontracted product
        picking = pickings.filtered(lambda p: p.state == "subcontracted")
        product_ids = (
            picking.move_ids_without_package.mapped("product_id").sorted("id").ids
        )
        self.assertEqual(
            [self.product_plate_id.id],
            product_ids,
            msg="'Plate' must be in the picking",
        )
