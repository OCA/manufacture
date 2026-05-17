from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, TransactionCase


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

    def test_bom_line_create_uom_inferred_from_template(self):
        """When only `component_template_id` is provided (no product_uom_id),
        the create override sets the UoM from the template."""
        line = self.env["mrp.bom.line"].create(
            {
                "bom_id": self.bom.id,
                "component_template_id": self.plastic.id,
                "product_qty": 1.0,
            }
        )
        self.assertEqual(line.product_uom_id, self.plastic.uom_id)
        self.assertFalse(line.product_id)

    def test_onchange_component_template_backups_and_restores_product(self):
        """Setting the template stashes the original product; clearing it back
        restores the stashed value."""
        plastic_red = self._plastic_variant(self.color_red)
        with Form(self.env["mrp.bom"]) as bom_form:
            bom_form.product_tmpl_id = self.finished
            with bom_form.bom_line_ids.new() as line_form:
                line_form.product_id = plastic_red
                line_form.product_qty = 1.0
                # Setting the template empties product_id and backs it up.
                line_form.component_template_id = self.plastic
                self.assertFalse(line_form.product_id)
                # Clearing the template restores the original product.
                line_form.component_template_id = self.env["product.template"]
                self.assertEqual(line_form.product_id, plastic_red)

    def test_get_component_or_product_id_no_template_returns_line_product(self):
        """When the bom line has no component_template_id, the resolver is a
        no-op that returns the original line product."""
        plastic_red = self._plastic_variant(self.color_red)
        finished_red = self._finished_variant(self.color_red)
        bom_static = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": plastic_red.id,
                            "product_qty": 1.0,
                        },
                    )
                ],
            }
        )
        resolved = bom_static._get_component_or_product_id(
            bom_static.bom_line_ids, finished_red, plastic_red
        )
        self.assertEqual(resolved, plastic_red)

    def test_explode_skips_dynamic_line_when_variant_does_not_exist(self):
        """Parent variant carries an attribute value that the component
        template does not have — line is skipped, not raised."""
        green = self.env["product.attribute.value"].create(
            {"name": "Green", "attribute_id": self.color.id}
        )
        # Add Green only to the finished product, NOT to plastic.
        self.finished.attribute_line_ids.write({"value_ids": [(4, green.id)]})
        finished_green = self.finished.product_variant_ids.filtered(
            lambda v: green
            in v.product_template_attribute_value_ids.product_attribute_value_id
        )
        self.assertTrue(finished_green)
        _boms, lines = self.bom.explode(finished_green, 1)
        self.assertEqual(
            lines, [], "Dynamic line must be skipped when no variant matches."
        )

    def test_explode_no_dynamic_components_takes_the_pass_through_path(self):
        """A BoM without `component_template_id` lines still explodes
        correctly and does not virtualise."""
        plastic_red = self._plastic_variant(self.color_red)
        finished_red = self._finished_variant(self.color_red)
        bom_static = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {"product_id": plastic_red.id, "product_qty": 2.0},
                    )
                ],
            }
        )
        self.assertFalse(bom_static._has_dynamic_components())
        _boms, lines = bom_static.explode(finished_red, 1)
        self.assertEqual(len(lines), 1)
        line, vals = lines[0]
        self.assertEqual(line.product_id, plastic_red)
        self.assertEqual(vals["qty"], 2.0)

    def test_match_on_attribute_ids_cleared_when_template_removed(self):
        """Removing the component template empties the computed match list."""
        self.assertEqual(self.bom_line.match_on_attribute_ids, self.color)
        # Write a real product on the line, clearing the template via onchange
        # is covered by the dedicated Form test above; here we just clear it.
        self.bom_line.component_template_id = False
        self.assertFalse(self.bom_line.match_on_attribute_ids)

    def test_template_attribute_removal_blocked_when_used_in_match(self):
        """Removing the matched attribute from the parent template (while
        keeping other attributes on it) must fail, because the BoM line
        still references the removed attribute in match_on_attribute_ids.
        """
        material = self.env["product.attribute"].create(
            {"name": "Material", "create_variant": "always"}
        )
        wood = self.env["product.attribute.value"].create(
            {"name": "Wood", "attribute_id": material.id}
        )
        # First write: add Material to the finished product. Passes the
        # constraint because Color is still there.
        self.finished.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": material.id,
                            "value_ids": [(6, 0, [wood.id])],
                        },
                    )
                ]
            }
        )
        color_line = self.finished.attribute_line_ids.filtered(
            lambda line: line.attribute_id == self.color
        )
        # Second write: remove the Color line. Now match_on_attribute_ids
        # (= Color) is no longer covered by the parent's attributes.
        with self.assertRaises(UserError):
            self.finished.write({"attribute_line_ids": [(2, color_line.id)]})

    def test_template_used_as_component_must_not_add_unknown_attribute(self):
        """Adding an attribute to the component that the parent template does
        not have breaks the matching contract."""
        smell = self.env["product.attribute"].create(
            {"name": "Smell", "create_variant": "always"}
        )
        smell_orchid = self.env["product.attribute.value"].create(
            {"name": "Orchid", "attribute_id": smell.id}
        )
        with self.assertRaises(UserError):
            self.plastic.write(
                {
                    "attribute_line_ids": [
                        (
                            0,
                            0,
                            {
                                "attribute_id": smell.id,
                                "value_ids": [(6, 0, [smell_orchid.id])],
                            },
                        )
                    ]
                }
            )

    def test_bom_structure_report_resolves_dynamic_component(self):
        """The BoM structure report must show the resolved variant for a
        dynamic-component line, and not crash on the in-memory bom copy."""
        finished_red = self._finished_variant(self.color_red)
        plastic_red = self._plastic_variant(self.color_red)
        warehouse = self.env.ref("stock.warehouse0")
        report = self.env["report.mrp.report_bom_structure"]
        data = report._get_bom_data(self.bom, warehouse, product=finished_red, level=0)
        component_product_ids = [
            c.get("product_id") for c in data.get("components", [])
        ]
        self.assertIn(plastic_red.id, component_product_ids)

    def test_action_confirm_creates_raw_move_for_resolved_variant(self):
        """Confirming the MO must generate a raw move pointing at the
        resolved plastic variant and leave the BoM line product_id empty."""
        finished_red = self._finished_variant(self.color_red)
        plastic_red = self._plastic_variant(self.color_red)
        # Order mirrors the 18.0 module's tests: product → bom → qty,
        # to avoid the qty re-computation that the bom_id onchange runs.
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = finished_red
        mo_form.bom_id = self.bom
        mo_form.product_qty = 1.0
        mo = mo_form.save()
        mo.action_confirm()
        self.assertEqual(len(mo.move_raw_ids), 1)
        self.assertEqual(mo.move_raw_ids.product_id, plastic_red)
        # The BoM line was not mutated by the confirmation flow.
        self.bom_line.invalidate_recordset()
        self.assertFalse(self.bom_line.product_id)
