from odoo.tests import tagged
from odoo.tests.common import Form, SavepointCase


@tagged("post_install", "-at_install")
class TestMrpSubcontractingReorderingRules(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # 1: Create a subcontracting partner
        main_partner = cls.env["res.partner"].create({"name": "main_partner"})
        cls.subcontractor_partner1 = cls.env["res.partner"].create(
            {
                "name": "subcontractor_partner",
                "parent_id": main_partner.id,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )

        form = Form(cls.env["product.template"])
        form.name = "Product For Subcontractor"
        form.type = "product"
        cls.product_template = form.save()

        # 2. Create a BOM of subcontracting type
        cls.comp1 = cls.env["product.product"].create(
            {
                "name": "Component1",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.comp2 = cls.env["product.product"].create(
            {
                "name": "Component2",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.finished = cls.env["product.product"].create(
            {
                "name": "finished",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.type = "subcontract"
        bom_form.product_tmpl_id = cls.finished.product_tmpl_id
        bom_form.subcontractor_ids.add(cls.subcontractor_partner1)
        with bom_form.bom_line_ids.new() as bom_line:
            bom_line.product_id = cls.comp1
            bom_line.product_qty = 1
        with bom_form.bom_line_ids.new() as bom_line:
            bom_line.product_id = cls.comp2
            bom_line.product_qty = 1
        cls.bom = bom_form.save()

        # Create a BoM for cls.comp2
        cls.comp2comp = cls.env["product.product"].create(
            {
                "name": "component for Component2",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.product_tmpl_id = cls.comp2.product_tmpl_id
        with bom_form.bom_line_ids.new() as bom_line:
            bom_line.product_id = cls.comp2comp
            bom_line.product_qty = 1
        cls.comp2_bom = bom_form.save()

    def test_product_supplierinfo_create_unlink(self):
        product_supplierinfo = self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.finished.product_tmpl_id.id,
                "name": self.subcontractor_partner1.id,
            }
        )

        product_supplierinfo._compute_update_orderpoints()
        orderpoints = product_supplierinfo.product_tmpl_id.mapped(
            "product_variant_ids.orderpoint_ids"
        )
        self.assertTrue(orderpoints)
        self.assertEqual(orderpoints[0].trigger, "manual", msg="Must be equal 'manual'")

        product_supplierinfo.write({"trigger": "auto"})
        product_supplierinfo._compute_update_orderpoints()
        self.assertEqual(orderpoints[0].trigger, "auto", msg="Must be equal 'auto'")

        orderpoints_ids = orderpoints.ids
        product_supplierinfo.unlink()
        empty_orderpoints = self.env["stock.warehouse.orderpoint"].search(
            [("id", "in", orderpoints_ids)]
        )
        self.assertFalse(empty_orderpoints, msg="Recordset must be empty")

    def test_product_supplierinfo_orderpoints(self):
        product_supplierinfo = self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.finished.product_tmpl_id.id,
                "product_id": self.finished.id,
                "name": self.subcontractor_partner1.id,
            }
        )
        product_supplierinfo._compute_update_orderpoints()
        orderpoints = product_supplierinfo.with_context(
            active_test=False
        ).order_points_ids
        self.assertRecordValues(
            orderpoints,
            [
                {
                    "location_id": product_supplierinfo.name.property_stock_subcontractor.id,
                    "route_id": product_supplierinfo.route_id.id,
                    "trigger": product_supplierinfo.trigger,
                    "active": True,
                }
            ],
        )

    def test_product_supplierinfo_inactive(self):
        product_supplierinfo = self.env["product.supplierinfo"].create(
            {
                "product_id": self.finished.id,
                "name": self.subcontractor_partner1.id,
            }
        )
        product_supplierinfo._compute_update_orderpoints()
        orderpoints = product_supplierinfo.with_context(
            active_test=False
        ).order_points_ids
        self.assertFalse(orderpoints.active, msg="Order point active must be true")

    def test_product_supplier_info_create_sw_order_point(self):
        product_supplierinfo = self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.finished.product_tmpl_id.id,
                "product_id": self.finished.id,
                "name": self.subcontractor_partner1.id,
            }
        )
        product_supplierinfo.with_context(active_test=False).order_points_ids.unlink()
        self.assertFalse(
            product_supplierinfo.order_points_ids, msg="Order points must be empty"
        )
        product_supplierinfo._compute_update_orderpoints()
        orderpoint = product_supplierinfo.order_points_ids
        self.assertRecordValues(
            orderpoint,
            [
                {
                    "product_id": self.finished.id,
                    "product_min_qty": 0,
                    "product_max_qty": 0,
                    "qty_multiple": 1,
                    "location_id": product_supplierinfo.name.property_stock_subcontractor.id,
                    "route_id": product_supplierinfo.route_id.id,
                    "trigger": product_supplierinfo.trigger,
                    "supplier_id": product_supplierinfo.id,
                }
            ],
        )
