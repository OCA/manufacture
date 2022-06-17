from odoo.tests import Form, common


class TestMrpAttachmentMgmtBase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_products(cls)
        cls._create_boms(cls)

    def _create_products(self):
        self.warehouse = self.env.ref("stock.warehouse0")
        route_manufacture = self.warehouse.manufacture_pull_id.route_id.id
        self.product_sword = self.env["product.template"].create(
            {
                "name": "Plastic Sword",
                "type": "product",
            }
        )
        self.product_surf = self.env["product.template"].create(
            {
                "name": "Surf",
                "type": "product",
            }
        )
        self.product_fin = self.env["product.template"].create(
            {
                "name": "Surf Fin",
                "type": "product",
            }
        )
        self.product_plastic = self.env["product.template"].create(
            {
                "name": "Plastic Component",
                "type": "product",
            }
        )
        self.p1 = self.env["product.template"].create(
            {
                "name": "P1",
                "type": "product",
                "route_ids": [(6, 0, [route_manufacture])],
            }
        )
        self.p2 = self.env["product.template"].create(
            {
                "name": "P2",
                "type": "product",
                "route_ids": [(6, 0, [route_manufacture])],
            }
        )
        self.p3 = self.env["product.template"].create(
            {
                "name": "P3",
                "type": "product",
                "route_ids": [(6, 0, [route_manufacture])],
            }
        )
        self.product_9 = self.env["product.product"].create(
            {
                "name": "Paper",
            }
        )
        self.product_10 = self.env["product.product"].create(
            {
                "name": "Stone",
            }
        )
        self.product_attribute = self.env["product.attribute"].create(
            {"name": "Colour", "display_type": "radio", "create_variant": "always"}
        )
        self.attribute_value_ids = self.env["product.attribute.value"].create(
            [
                {"name": "Cyan", "attribute_id": self.product_attribute.id},
                {"name": "Magenta", "attribute_id": self.product_attribute.id},
            ]
        )
        self.plastic_attrs = self.env["product.template.attribute.line"].create(
            {
                "attribute_id": self.product_attribute.id,
                "product_tmpl_id": self.product_plastic.id,
                "value_ids": [(6, 0, self.product_attribute.value_ids.ids)],
            }
        )
        self.sword_attrs = self.env["product.template.attribute.line"].create(
            {
                "attribute_id": self.product_attribute.id,
                "product_tmpl_id": self.product_sword.id,
                "value_ids": [(6, 0, self.product_attribute.value_ids.ids)],
            }
        )

    def _create_boms(self):
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product_sword
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.component_template_id = self.product_plastic
            line_form.product_qty = 1
        self.bom_id = mrp_bom_form.save()

        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product_fin
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.product_plastic.product_variant_ids[0]
            line_form.product_qty = 1
        self.fin_bom_id = mrp_bom_form.save()

        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product_surf
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.product_fin.product_variant_ids[0]
            line_form.product_qty = 1
        self.surf_bom_id = mrp_bom_form.save()

        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.p1
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.p2.product_variant_ids[0]
            line_form.product_qty = 1
        self.p1_bom_id = mrp_bom_form.save()

        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.p2
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.p3.product_variant_ids[0]
            line_form.product_qty = 1
        self.p2_bom_id = mrp_bom_form.save()

        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.p3
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.p1.product_variant_ids[0]
            line_form.product_qty = 1
        self.p3_bom_id = mrp_bom_form.save()
