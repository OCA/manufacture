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

    def test_explode_skips_line_when_apply_on_variants_does_not_match(self):
        """A line with `bom_product_template_attribute_value_ids` set is
        skipped by `_skip_bom_line` for variants outside that filter."""
        plastic_red = self._plastic_variant(self.color_red)
        finished_red = self._finished_variant(self.color_red)
        finished_blue = self._finished_variant(self.color_blue)
        red_ptav = self.finished.attribute_line_ids.product_template_value_ids.filtered(
            lambda v: v.product_attribute_value_id == self.color_red
        )
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
                            "bom_product_template_attribute_value_ids": [
                                (6, 0, red_ptav.ids)
                            ],
                        },
                    )
                ],
            }
        )
        _boms, lines_red = bom_static.explode(finished_red, 1)
        self.assertEqual(len(lines_red), 1, "Red variant must consume the line.")
        _boms, lines_blue = bom_static.explode(finished_blue, 1)
        self.assertEqual(lines_blue, [], "Blue variant must skip the Red-only line.")

    def test_get_component_or_product_id_returns_empty_for_inactive_variant(self):
        """When the matched variant exists but is archived, the resolver
        returns an empty recordset so the line is silently skipped."""
        plastic_red = self._plastic_variant(self.color_red)
        finished_red = self._finished_variant(self.color_red)
        plastic_red.active = False
        resolved = self.bom._get_component_or_product_id(
            self.bom_line, finished_red, self.bom_line.product_id
        )
        self.assertFalse(resolved)

    def test_match_on_attribute_ids_excludes_no_variant_attribute(self):
        """Component template attributes with `create_variant='no_variant'`
        must not appear in match_on_attribute_ids."""
        finish = self.env["product.attribute"].create(
            {"name": "Finish", "create_variant": "no_variant"}
        )
        matte = self.env["product.attribute.value"].create(
            {"name": "Matte", "attribute_id": finish.id}
        )
        # Add Finish to BOTH templates so the cross-template constraint passes.
        self.finished.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": finish.id,
                            "value_ids": [(6, 0, [matte.id])],
                        },
                    )
                ]
            }
        )
        self.plastic.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": finish.id,
                            "value_ids": [(6, 0, [matte.id])],
                        },
                    )
                ]
            }
        )
        # _compute_match_on_attribute_ids depends on component_template_id
        # alone, so we re-trigger it explicitly after changing the template.
        self.bom_line._compute_match_on_attribute_ids()
        self.assertIn(self.color, self.bom_line.match_on_attribute_ids)
        self.assertNotIn(finish, self.bom_line.match_on_attribute_ids)

    def test_action_confirm_on_static_bom_keeps_real_bom_line_fk(self):
        """For a non-dynamic BoM, `bom_line.id` is a real int and the
        override of `_get_move_raw_values` does not rewrite it."""
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
                        {"product_id": plastic_red.id, "product_qty": 1.0},
                    )
                ],
            }
        )
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = finished_red
        mo_form.bom_id = bom_static
        mo_form.product_qty = 1.0
        mo = mo_form.save()
        mo.action_confirm()
        self.assertEqual(mo.move_raw_ids.bom_line_id, bom_static.bom_line_ids)

    def test_explode_detects_cycle_through_phantom_subbom(self):
        """`explode()` must catch a cycle when a phantom sub-BoM points back
        to the BoM's own product. The root BoM is `type='normal'` so that
        core's `_check_bom_cycle` (which only traverses phantom sub-BoMs)
        does not block the setup; the sub-BoM is `type='phantom'` so that
        explode follows it and the dependency graph closes the cycle.
        Mirrors the pattern used by `test_bom_recursion` in the 18.0
        version of the module.
        """
        tmpl_a = self.env["product.template"].create(
            {"name": "Cycle A", "type": "product"}
        )
        tmpl_b = self.env["product.template"].create(
            {"name": "Cycle B", "type": "product"}
        )
        product_a = tmpl_a.product_variant_ids
        product_b = tmpl_b.product_variant_ids
        bom_a = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": tmpl_a.id,
                "product_id": product_a.id,
                "type": "normal",
                "product_qty": 1.0,
                "product_uom_id": product_a.uom_id.id,
            }
        )
        bom_b = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": tmpl_b.id,
                "product_id": product_b.id,
                "type": "phantom",
                "product_qty": 1.0,
                "product_uom_id": product_b.uom_id.id,
            }
        )
        # Lines added separately so core's cycle constraint runs against
        # an incremental tree where the phantom for product_a doesn't yet
        # exist as a phantom (bom_a is normal).
        self.env["mrp.bom.line"].create(
            {
                "bom_id": bom_a.id,
                "product_id": product_b.id,
                "product_qty": 1.0,
                "product_uom_id": product_b.uom_id.id,
            }
        )
        self.env["mrp.bom.line"].create(
            {
                "bom_id": bom_b.id,
                "product_id": product_a.id,
                "product_qty": 1.0,
                "product_uom_id": product_a.uom_id.id,
            }
        )
        with self.assertRaises(UserError):
            bom_a.explode(product_a, 1)

    def test_bom_structure_report_skips_unmatched_dynamic_line(self):
        """The BoM structure report must omit dynamic lines for which the
        component template has no variant matching the parent's variant."""
        green = self.env["product.attribute.value"].create(
            {"name": "Green", "attribute_id": self.color.id}
        )
        # Add Green only to the finished product; plastic does not have it.
        self.finished.attribute_line_ids.write({"value_ids": [(4, green.id)]})
        finished_green = self.finished.product_variant_ids.filtered(
            lambda v: green
            in v.product_template_attribute_value_ids.product_attribute_value_id
        )
        warehouse = self.env.ref("stock.warehouse0")
        report = self.env["report.mrp.report_bom_structure"]
        data = report._get_bom_data(
            self.bom, warehouse, product=finished_green, level=0
        )
        self.assertEqual(
            data.get("components", []),
            [],
            "Dynamic line without a matching variant must be skipped.",
        )

    def test_onchange_bom_product_template_attribute_value_via_form_raises(self):
        """The onchange handler `_onchange_bom_product_template_attribute_
        value_ids_check_variants` must fire when adding an overlapping
        attribute via Form and propagate the validation error."""
        red_ptav = self.finished.attribute_line_ids.product_template_value_ids.filtered(
            lambda v: v.product_attribute_value_id == self.color_red
        )
        with self.assertRaises(ValidationError):
            with Form(self.bom) as bom_form:
                with bom_form.bom_line_ids.edit(0) as line_form:
                    line_form.bom_product_template_attribute_value_ids.add(red_ptav)

    def test_check_component_attributes_raises_when_template_has_no_attributes(self):
        """A template with no attribute lines cannot be used as a dynamic
        component — the first raise in `_check_component_attributes` fires."""
        empty_template = self.env["product.template"].create(
            {"name": "Plastic No Attrs", "type": "product"}
        )
        with self.assertRaises(ValidationError):
            self.env["mrp.bom.line"].create(
                {
                    "bom_id": self.bom.id,
                    "component_template_id": empty_template.id,
                    "product_qty": 1.0,
                }
            )

    def test_onchange_component_template_realigns_uom_in_both_directions(self):
        """Setting a template whose UoM is in a different category must
        switch the line's UoM, and clearing the template must restore it
        from the backed-up product. Uses `.new()` + manual onchange call
        because the form view does not expose `product_uom_id` inside the
        bom_line tree when only the inherited fields are present.
        """
        kg = self.env.ref("uom.product_uom_kgm")
        units = self.env.ref("uom.product_uom_unit")
        plastic_red = self._plastic_variant(self.color_red)  # uom = units
        plastic_kg = self.env["product.template"].create(
            {
                "name": "Plastic KG",
                "type": "product",
                "uom_id": kg.id,
                "uom_po_id": kg.id,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.color.id,
                            "value_ids": [
                                (6, 0, [self.color_red.id, self.color_blue.id])
                            ],
                        },
                    )
                ],
            }
        )
        line = self.env["mrp.bom.line"].new(
            {
                "bom_id": self.bom.id,
                "product_id": plastic_red.id,
                "product_uom_id": units.id,
            }
        )
        # Step 1: assign the kg template — product is backed up and UoM
        # realigns from units → kg.
        line.component_template_id = plastic_kg
        line._onchange_component_template_id()
        self.assertFalse(line.product_id)
        self.assertEqual(line.product_uom_id, kg)
        # Step 2: clear the template — product is restored and UoM realigns
        # back from kg → units.
        line.component_template_id = self.env["product.template"]
        line._onchange_component_template_id()
        self.assertEqual(line.product_id, plastic_red)
        self.assertEqual(line.product_uom_id, units)
