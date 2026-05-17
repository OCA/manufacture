from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestMrpBomAttributeMatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Shared "Color" attribute on parent product and component template,
        # so the dynamic match has something to resolve.
        cls.color = cls.env["product.attribute"].create(
            {"name": "Color", "create_variant": "always"}
        )
        cls.color_red = cls.env["product.attribute.value"].create(
            {"name": "Red", "attribute_id": cls.color.id}
        )
        cls.color_blue = cls.env["product.attribute.value"].create(
            {"name": "Blue", "attribute_id": cls.color.id}
        )

        cls.finished = cls.env["product.template"].create(
            {
                "name": "Finished Sword",
                "type": "product",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.color.id,
                            "value_ids": [
                                (6, 0, [cls.color_red.id, cls.color_blue.id])
                            ],
                        },
                    )
                ],
            }
        )
        cls.plastic = cls.env["product.template"].create(
            {
                "name": "Plastic",
                "type": "product",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.color.id,
                            "value_ids": [
                                (6, 0, [cls.color_red.id, cls.color_blue.id])
                            ],
                        },
                    )
                ],
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "component_template_id": cls.plastic.id,
                            "product_qty": 1.0,
                            "product_uom_id": cls.plastic.uom_id.id,
                        },
                    )
                ],
            }
        )
        cls.bom_line = cls.bom.bom_line_ids

    def _finished_variant(self, value):
        return self.finished.product_variant_ids.filtered(
            lambda v: value
            in v.product_template_attribute_value_ids.product_attribute_value_id
        )

    def _plastic_variant(self, value):
        return self.plastic.product_variant_ids.filtered(
            lambda v: value
            in v.product_template_attribute_value_ids.product_attribute_value_id
        )

    def test_explode_resolves_dynamic_component(self):
        """explode() must return lines pointing at the resolved variant."""
        finished_red = self._finished_variant(self.color_red)
        plastic_red = self._plastic_variant(self.color_red)
        _boms, lines = self.bom.explode(finished_red, 1)
        self.assertEqual(len(lines), 1)
        resolved_line, _vals = lines[0]
        self.assertEqual(resolved_line.product_id, plastic_red)

    def test_explode_does_not_mutate_bom(self):
        """The persisted bom.line must not have its product_id written to."""
        finished_red = self._finished_variant(self.color_red)
        self.assertFalse(self.bom_line.product_id)
        self.bom.explode(finished_red, 1)
        # Re-read from the DB to be sure no flush happened behind our back.
        self.bom_line.invalidate_recordset()
        self.assertFalse(
            self.bom_line.product_id,
            "explode() must not persist resolved variants on the source BoM line.",
        )

    def test_explode_skips_line_when_no_variant_matches(self):
        """If the parent product has no compatible attribute combination,
        the dynamic line is skipped instead of raising or matching wrong."""
        plain = self.env["product.template"].create(
            {"name": "Plain Sword", "type": "product"}
        )
        bom_plain = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": plain.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        # Cannot use the component template on a parent with no shared attribute:
        # the validation constraint should reject it.
        with self.assertRaises(ValidationError):
            self.env["mrp.bom.line"].create(
                {
                    "bom_id": bom_plain.id,
                    "component_template_id": self.plastic.id,
                    "product_qty": 1.0,
                    "product_uom_id": self.plastic.uom_id.id,
                }
            )

    def test_apply_on_variants_cannot_overlap_match_attribute(self):
        """Using the matched attribute also as 'Apply on Variants' must fail."""
        red_ptav = self.finished.attribute_line_ids.product_template_value_ids.filtered(
            lambda v: v.product_attribute_value_id == self.color_red
        )
        with self.assertRaises(ValidationError):
            self.bom_line.write(
                {"bom_product_template_attribute_value_ids": [(6, 0, red_ptav.ids)]}
            )
