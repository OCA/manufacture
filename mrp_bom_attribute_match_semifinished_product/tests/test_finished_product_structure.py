from odoo.exceptions import MissingError, UserError
from odoo.tests import Form

from .test_finished_product_common import TestFinishedProductCommon


class TestFinishedProductStructure(TestFinishedProductCommon):
    def setUp(self):
        super(TestFinishedProductStructure, self).setUp()
        self.size_attr = self.env["product.attribute"].create({"name": "Size"})
        self.size_attr_value_s = self.env["product.attribute.value"].create(
            {"name": "S", "attribute_id": self.size_attr.id}
        )
        self.size_attr_value_m = self.env["product.attribute.value"].create(
            {"name": "M", "attribute_id": self.size_attr.id}
        )
        self.size_attr_value_l = self.env["product.attribute.value"].create(
            {"name": "L", "attribute_id": self.size_attr.id}
        )
        form = Form(self.env["product.template"])
        form.name = "Product #1"
        form.finished_product = True
        with form.attribute_line_ids.new() as attribute:
            attribute.attribute_id = self.color_attribute
            attribute.value_ids.add(self.color_white_attr_value)
            attribute.value_ids.add(self.color_black_attr_value)
        self.product_2 = form.save()

        form = Form(self.env["product.template"])
        form.name = "Product #1"
        form.finished_product = True
        with form.attribute_line_ids.new() as attribute:
            attribute.attribute_id = self.legs_attribute
            attribute.value_ids.add(self.legs_steel_attr_value)
            attribute.value_ids.add(self.legs_aluminium_attr_value)
        self.product_3 = form.save()

        self.stage_1_product = self.env["product.template"].create(
            {"name": "Product #1 Stage #1"}
        )
        self.stage_2_product = self.env["product.template"].create(
            {"name": "Product #2 Stage #2"}
        )

        self.partner_subcontractor = self.env["res.partner"].create(
            {"name": "Subcontractor #1"}
        )
        self.product_shirt_template = self.env["product.template"].create(
            {
                "name": "Shirt",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.size_attr.id,
                            "value_ids": [(6, 0, [self.size_attr_value_l.id])],
                        },
                    )
                ],
            }
        )

    def test_structure_without_lines(self):
        form = Form(
            self.env["finished.product.structure.wizard"].with_context(
                default_finished_product_id=self.product_1.id
            )
        )
        wizard = form.save()
        with self.assertRaises(MissingError):
            wizard.create_product_struct()

    def test_structure_check_attributes(self):
        with Form(
            self.env["finished.product.structure.wizard"].with_context(
                default_finished_product_id=self.product_1.id
            )
        ) as form:
            attribute_ids = form._values.get("attribute_ids")[0][2]
            self.assertListEqual(
                attribute_ids,
                [self.legs_attribute.id, self.color_attribute.id],
                msg="List attributes IDS must be the same",
            )
            form.finished_product_id = self.product_2
            attribute_ids = form._values.get("attribute_ids")[0][2]
            self.assertListEqual(
                attribute_ids,
                self.color_attribute.ids,
                msg="List attributes IDS must be the same",
            )
            form.finished_product_id = self.product_3
            attribute_ids = form._values.get("attribute_ids")[0][2]
            self.assertListEqual(
                attribute_ids,
                self.legs_attribute.ids,
                msg="List attributes IDS must be the same",
            )
            with self.assertRaises(UserError), form.line_ids.new() as line:
                line.stage_name = "Stage 1"
                line.product_tmpl_id = self.product_shirt_template
                line.bom_type = "normal"

    def test_tmp_product_struct_line(self):
        wizard = self.env["finished.product.structure.wizard"].create(
            {"finished_product_id": self.product_1.id}
        )
        tmp_record = wizard._tmp_product_struct_line()
        self.assertRecordValues(
            tmp_record,
            [
                {
                    "stage_name": "{} - Start".format(self.product_1.name),
                    "product_tmpl_id": self.product_1.id,
                    "product_tmpl_stage_id": self.product_1.id,
                }
            ],
        )

    def _create_product_struct(self, product_id):
        form = Form(
            self.env["finished.product.structure.wizard"].with_context(
                default_finished_product_id=product_id
            )
        )
        with form.line_ids.new() as line:
            line.stage_name = "Stage #1"
            line.product_tmpl_id = self.stage_1_product
            line.bom_type = "normal"
        with form.line_ids.new() as line:
            line.stage_name = "Stage #2"
            line.product_tmpl_id = self.stage_2_product
            line.bom_type = "normal"
        return form.save()

    def test_create_product_struct(self):
        wizard = self._create_product_struct(self.product_1.id)
        result = wizard.create_product_struct()
        self.assertDictEqual(
            result,
            {"type": "ir.actions.act_window_close"},
            msg="Dicts must be the same",
        )
        self.assertEqual(
            len(self.product_1.semi_finished_product_tmpl_ids),
            2,
            msg="Products count must be equal to 2",
        )
        product_line_1, product_line_2 = self.product_1.semi_finished_product_tmpl_ids
        self.assertEqual(
            len(self.product_1.semi_finished_mrp_bom_ids),
            2,
            msg="BOM's count must be equal to 2",
        )
        bom_1, bom_2 = self.product_1.semi_finished_mrp_bom_ids
        # Bom 1
        self.assertEqual(
            bom_1.product_tmpl_id,
            self.product_1,
            msg="Bom product must be equal to ID #{}".format(self.product_1.id),
        )
        line_ids = bom_1.bom_line_ids
        self.assertEqual(
            line_ids.component_template_id,
            product_line_1.semi_finished_product_tmpl_id,
            msg="Bom component product must be equal to ID #{}".format(
                product_line_1.semi_finished_product_tmpl_id.id
            ),
        )
        self.assertListEqual(
            line_ids.match_on_attribute_ids.ids,
            [self.legs_attribute.id, self.color_attribute.id],
            msg="Attributes must be the same",
        )
        # Bom 2
        self.assertEqual(
            bom_2.product_tmpl_id,
            product_line_1.semi_finished_product_tmpl_id,
            msg="Bom product must be equal to ID #{}".format(
                product_line_1.semi_finished_product_tmpl_id.id
            ),
        )
        line_ids = bom_2.bom_line_ids
        self.assertEqual(
            line_ids.component_template_id,
            product_line_2.semi_finished_product_tmpl_id,
            msg="Bom component product must be equal to ID #{}".format(
                product_line_2.semi_finished_product_tmpl_id.id
            ),
        )
        self.assertListEqual(
            line_ids.match_on_attribute_ids.ids,
            [self.legs_attribute.id, self.color_attribute.id],
            msg="Attributes must be the same",
        )

    def test_recreate_product_struct(self):
        wizard = self._create_product_struct(self.product_1.id)
        wizard.create_product_struct()
        semi_first_product_ids = self.product_1.semi_finished_product_tmpl_ids.ids
        bom_first_ids = self.product_1.semi_finished_product_tmpl_ids.ids
        # Recreate structure
        wizard = self._create_product_struct(self.product_1.id)
        wizard.create_product_struct()
        semi_second_product_ids = self.product_1.semi_finished_product_tmpl_ids.ids
        bom_second_ids = self.product_1.semi_finished_product_tmpl_ids.ids
        self.assertNotEqual(semi_first_product_ids, semi_second_product_ids)
        self.assertNotEqual(bom_first_ids, bom_second_ids)

    def test_prepare_bom_by_products(self):
        form = Form(
            self.env["finished.product.structure.wizard"].with_context(
                default_finished_product_id=self.product_1
            )
        )
        with form.line_ids.new() as line:
            line.stage_name = "Stage #1"
            line.product_tmpl_id = self.stage_1_product
            line.bom_type = "normal"
        with form.line_ids.new() as line:
            line.stage_name = "Stage #2"
            line.product_tmpl_id = self.stage_2_product
            line.bom_type = "subcontract"
            line.partner_ids.add(self.partner_subcontractor)
        wizard = form.save()
        vals = wizard._prepare_bom_by_products()
        bom_1_vals, bom_2_vals = vals
        self.assertEqual(
            bom_1_vals.get("product_tmpl_id"),
            self.product_1.id,
            msg="Product Template must be equal to ID #{}".format(self.product_1.id),
        )
        self.assertEqual(
            bom_1_vals.get("type"), "normal", msg="Bom type must be equal to normal"
        )
        self.assertFalse(
            bom_2_vals.get("product_tmpl_id"), msg="Product Template not set"
        )
        self.assertEqual(
            bom_2_vals.get("type"),
            "subcontract",
            msg="Bom type must be equal to 'subcontract'",
        )
        self.assertEqual(
            bom_2_vals.get("subcontractor_ids")[0][2],
            self.partner_subcontractor.ids,
            msg="Partner subcontractor must be contains in bom vals",
        )
