from .common import TestMrpBomAttributeMatchBase


class TestMrpBomAttributeMatchNested(TestMrpBomAttributeMatchBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def setUp(self):
        super().setUp()
        attr1 = self.env["product.attribute"].create(
            {"name": "style", "display_type": "radio", "create_variant": "always"}
        )
        a1vs = self.env["product.attribute.value"].create(
            [
                {"name": "office", "attribute_id": attr1.id},
                {"name": "gaming", "attribute_id": attr1.id},
            ]
        )

        top = self.env["product.template"].create(
            {
                "name": "Top-Level",
                "type": "product",
            }
        )
        self.env["product.template.attribute.line"].create(
            {
                "attribute_id": attr1.id,
                "product_tmpl_id": top.id,
                "value_ids": [(6, 0, a1vs.ids)],
            }
        )

        sub = self.env["product.template"].create(
            {
                "name": "Sub-Level",
                "type": "product",
            }
        )
        self.env["product.template.attribute.line"].create(
            {
                "attribute_id": attr1.id,
                "product_tmpl_id": sub.id,
                "value_ids": [(6, 0, a1vs.ids)],
            }
        )

        subsub = self.env["product.template"].create(
            {
                "name": "Sub Sub 1",
                "type": "product",
            }
        )
        self.env["product.template.attribute.line"].create(
            {
                "attribute_id": attr1.id,
                "product_tmpl_id": subsub.id,
                "value_ids": [(6, 0, a1vs.ids)],
            }
        )

        self.bom_sub = self._create_bom(
            sub,
            [
                dict(
                    component_template_id=subsub.id,
                    product_qty=1,
                ),
            ],
        )
        self.bom_top = self._create_bom(
            top,
            [
                dict(
                    component_template_id=sub.id,
                    product_qty=1,
                ),
            ],
        )

    def test_nested(self):
        self.env["mrp.routing.workcenter"].create(
            [
                {
                    "name": "Operation 1",
                    "workcenter_id": self.env.ref("mrp.mrp_workcenter_1").id,
                    "bom_id": self.bom_top.id,
                },
                {
                    "name": "Operation 2",
                    "workcenter_id": self.env.ref("mrp.mrp_workcenter_2").id,
                    "bom_id": self.bom_top.id,
                },
                {
                    "name": "Operation 1",
                    "workcenter_id": self.env.ref("mrp.mrp_workcenter_1").id,
                    "bom_id": self.bom_sub.id,
                },
                {
                    "name": "Operation 2",
                    "workcenter_id": self.env.ref("mrp.mrp_workcenter_2").id,
                    "bom_id": self.bom_sub.id,
                },
            ]
        )
        BomStructureReport = self.env["report.mrp.report_bom_structure"]
        values_top = BomStructureReport._get_report_values(
            self.bom_top.ids,
            data={"variant": self.bom_top.product_tmpl_id.product_variant_id.id},
        )
        values_sub = BomStructureReport._get_report_values(
            self.bom_sub.ids,
            data={"variant": self.bom_sub.product_tmpl_id.product_variant_id.id},
        )
        self.assertIn("Sub Sub 1", str(values_top["docs"][0]["lines"]))
        self.assertIn("Sub-Level", str(values_top["docs"][0]["lines"]))
        self.assertIn("Sub Sub 1", str(values_sub["docs"][0]["lines"]))
        self.assertNotIn("Sub-Level", str(values_sub["docs"][0]["lines"]))
        BomStructureReport._get_report_data(self.bom_sub.id)
        BomStructureReport._get_report_data(self.bom_top.id)
