# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import Command
from odoo.tests import Form, TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestMrpSecondaryUnit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Secondary units are only round-tripped by forms for these groups.
        cls.env.user.groups_id |= (
            cls.env.ref("uom.group_uom")
            | cls.env.ref("mrp.group_mrp_byproducts")
            | cls.env.ref("product.group_product_variant")
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.finished, cls.pallet = cls._create_product("Finished", cls.uom_unit, 20)
        cls.component, cls.bag = cls._create_product("Component", cls.uom_kg, 5)
        cls.byproduct, cls.crate = cls._create_product("Byproduct", cls.uom_unit, 4)
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished.product_tmpl_id.id,
                "product_uom_id": cls.uom_unit.id,
                "secondary_uom_id": cls.pallet.id,
                "secondary_uom_qty": 1.0,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.component.id,
                            "product_uom_id": cls.uom_kg.id,
                            "secondary_uom_id": cls.bag.id,
                            "secondary_uom_qty": 2.0,
                        }
                    )
                ],
                "byproduct_ids": [
                    Command.create(
                        {
                            "product_id": cls.byproduct.id,
                            "product_uom_id": cls.uom_unit.id,
                            "secondary_uom_id": cls.crate.id,
                            "secondary_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )

    @classmethod
    def _create_unit(cls, template, factor, variant=None):
        return cls.env["product.secondary.unit"].create(
            {
                "name": f"Pack of {factor:g}",
                "product_tmpl_id": template.id,
                "product_id": variant.id if variant else False,
                "uom_id": cls.uom_unit.id,
                "factor": factor,
            }
        )

    @classmethod
    def _create_product(cls, name, uom, factor):
        product = cls.env["product.product"].create(
            {"name": name, "is_storable": True, "uom_id": uom.id, "uom_po_id": uom.id}
        )
        return product, cls._create_unit(product.product_tmpl_id, factor, product)

    def _new_production(self, product_qty=None):
        production_form = Form(self.env["mrp.production"])
        production_form.product_id = self.finished
        production_form.bom_id = self.bom
        if product_qty is not None:
            production_form.product_qty = product_qty
        return production_form.save()

    def _finished_move(self, production):
        return production.move_finished_ids.filtered(
            lambda m: m.product_id == self.finished
        )

    def _assert_secondary(self, record, unit, secondary_qty, qty, field="product_qty"):
        self.assertEqual(record.secondary_uom_id, unit)
        self.assertEqual(record.secondary_uom_qty, secondary_qty)
        self.assertAlmostEqual(record[field], qty, places=2)

    def _assert_move(self, move, unit, secondary_qty, qty):
        self._assert_secondary(move, unit, secondary_qty, qty, "product_uom_qty")

    def _view_secondary_uom_domain(self, model, view_xmlid, values):
        """Evaluate the domain of the header secondary unit of a form view."""
        arch = etree.fromstring(
            self.env[model].get_view(self.env.ref(view_xmlid).id)["arch"]
        )
        nodes = arch.xpath("//field[@name='secondary_uom_id'][not(ancestor::list)]")
        self.assertEqual(len(nodes), 1)
        return safe_eval(nodes[0].get("domain"), dict(values))

    def test_bom_secondary_qty_drives_product_qty(self):
        """The factor refers to the product UoM, whatever the UoM of the line."""
        line = self.bom.bom_line_ids
        self._assert_secondary(self.bom, self.pallet, 1.0, 20.0)
        self._assert_secondary(line, self.bag, 2.0, 10.0)
        self._assert_secondary(self.bom.byproduct_ids, self.crate, 1.0, 4.0)
        line.secondary_uom_qty = 3.0
        self.assertEqual(line.product_qty, 15.0)
        line.product_uom_id = self.uom_gram
        line.secondary_uom_qty = 1.0
        self.assertEqual(line.product_qty, 5000.0)
        self.bom.product_uom_id = self.uom_dozen
        self.bom.secondary_uom_qty = 1.0
        self.assertAlmostEqual(self.bom.product_qty, 20.0 / 12.0, places=2)
        self.bom.code = "Unrelated change"
        self.assertEqual(self.bom.secondary_uom_id, self.pallet)

    def test_bom_secondary_unit_defaults_from_products(self):
        self.finished.product_tmpl_id.stock_secondary_uom_id = self.pallet
        self.component.stock_secondary_uom_id = self.bag
        self.byproduct.stock_secondary_uom_id = self.crate
        with Form(self.env["mrp.bom"]) as bom_form:
            bom_form.product_tmpl_id = self.finished.product_tmpl_id
            self._assert_secondary(bom_form, self.pallet, 1.0, 20.0)
            with bom_form.bom_line_ids.new() as line_form:
                line_form.product_id = self.component
                self._assert_secondary(line_form, self.bag, 1.0, 5.0)
            with bom_form.byproduct_ids.new() as byproduct_form:
                byproduct_form.product_id = self.byproduct
                self._assert_secondary(byproduct_form, self.crate, 1.0, 4.0)

    def test_bom_secondary_unit_follows_variant(self):
        """Narrowing a saved BoM to a variant keeps its quantity to produce."""
        attribute = self.env["product.attribute"].create(
            {
                "name": "Size",
                "value_ids": [Command.create({"name": n}) for n in ("S", "L")],
            }
        )
        template = self.env["product.template"].create(
            {
                "name": "With variants",
                "is_storable": True,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [Command.set(attribute.value_ids.ids)],
                        }
                    )
                ],
            }
        )
        variant, other_variant = template.product_variant_ids
        template_unit = self._create_unit(template, 6)
        variant_unit = self._create_unit(template, 10, variant)
        template.stock_secondary_uom_id = template_unit
        variant.stock_secondary_uom_id = variant_unit
        with Form(self.env["mrp.bom"]) as bom_form:
            bom_form.product_tmpl_id = template
            self._assert_secondary(bom_form, template_unit, 1.0, 6.0)
            bom_form.secondary_uom_qty = 5.0
        with Form(bom_form.record) as bom_form:
            bom_form.product_id = other_variant
            self._assert_secondary(bom_form, template_unit, 5.0, 30.0)
            bom_form.product_id = variant
            self._assert_secondary(bom_form, variant_unit, 3.0, 30.0)

    def test_bom_line_secondary_unit_replaced_on_product_change(self):
        """A unit of the previous product would convert with a foreign factor."""
        self.byproduct.stock_secondary_uom_id = self.crate
        with Form(self.bom) as bom_form:
            with bom_form.bom_line_ids.edit(0) as line_form:
                line_form.product_id = self.finished
                self.assertFalse(line_form.secondary_uom_id)
                line_form.product_id = self.byproduct
                self.assertEqual(line_form.secondary_uom_id, self.crate)

    def test_bom_secondary_unit_picked_keeps_qty(self):
        """A line reset to zero would silently consume nothing."""
        line = self.bom.bom_line_ids
        line.secondary_uom_id = False
        line.product_qty = 10.0
        line.secondary_uom_id = self.bag
        self._assert_secondary(line, self.bag, 2.0, 10.0)
        big_bag = self._create_unit(self.component.product_tmpl_id, 10)
        with Form(self.bom) as bom_form:
            with bom_form.bom_line_ids.edit(0) as line_form:
                line_form.secondary_uom_id = big_bag
            with bom_form.bom_line_ids.new() as line_form:
                line_form.product_id = self.component
                line_form.product_qty = 10.0
                line_form.secondary_uom_id = self.bag
        line, new_line = self.bom.bom_line_ids
        self._assert_secondary(line, big_bag, 1.0, 10.0)
        self._assert_secondary(new_line, self.bag, 2.0, 10.0)
        with Form(self.env["mrp.bom"]) as bom_form:
            bom_form.product_tmpl_id = self.finished.product_tmpl_id
            bom_form.product_qty = 10.0
            bom_form.secondary_uom_id = self.pallet
            self._assert_secondary(bom_form, self.pallet, 0.5, 10.0)
            bom_form.product_uom_id = self.uom_dozen
            bom_form.secondary_uom_qty = 1.8
            self.assertEqual(bom_form.product_qty, 3.0)

    def test_secondary_unit_domains_offer_units_of_the_product(self):
        """A BoM without variant must match units carrying a product_id."""
        self.assertTrue(self.pallet.product_id)
        units = self.env["product.secondary.unit"]
        domain = self._view_secondary_uom_domain(
            "mrp.bom",
            "mrp.mrp_bom_form_view",
            {"product_tmpl_id": self.bom.product_tmpl_id.id, "product_id": False},
        )
        self.assertIn(self.pallet, units.search(domain))
        domain = self._view_secondary_uom_domain(
            "mrp.production",
            "mrp.mrp_production_form_view",
            {"product_id": self.finished.id},
        )
        self.assertIn(self.pallet, units.search(domain))

    def test_production_secondary_values_from_bom(self):
        production = self._new_production()
        self._assert_secondary(production, self.pallet, 1.0, 20.0)
        self._assert_move(production.move_raw_ids, self.bag, 2.0, 10.0)
        self._assert_move(production.move_byproduct_ids, self.crate, 1.0, 4.0)
        self._assert_move(self._finished_move(production), self.pallet, 1.0, 20.0)
        box = self._create_unit(self.finished.product_tmpl_id, 10)
        production.secondary_uom_id = box
        self._assert_move(self._finished_move(production), box, 2.0, 20.0)

    def test_production_secondary_qty_rescales(self):
        """Moves must not keep the secondary quantity of the previous quantity."""
        production = self._new_production(product_qty=60.0)
        self._assert_move(production.move_raw_ids, self.bag, 6.0, 30.0)
        self._assert_move(production.move_byproduct_ids, self.crate, 3.0, 12.0)
        production.product_qty = 40.0
        self._assert_move(production.move_raw_ids, self.bag, 4.0, 20.0)
        production.secondary_uom_qty = 3.0
        self.assertEqual(production.product_qty, 60.0)
        production.move_raw_ids.secondary_uom_qty = 5.0
        self.assertEqual(production.move_raw_ids.product_uom_qty, 25.0)

    def test_production_secondary_unit_picked_keeps_qty(self):
        self.finished.stock_secondary_uom_id = self.pallet
        with Form(self.env["mrp.production"]) as production_form:
            production_form.product_id = self.finished
            production_form.bom_id = self.bom
            production_form.secondary_uom_id = self.env["product.secondary.unit"]
            production_form.secondary_uom_id = self.pallet
            self._assert_secondary(production_form, self.pallet, 1.0, 20.0)
        self.bom.active = False
        with Form(self.env["mrp.production"]) as production_form:
            production_form.product_id = self.finished
            self.assertFalse(production_form.bom_id)
            self.assertEqual(production_form.secondary_uom_id, self.pallet)

    def test_production_non_dependent_units(self):
        """Secondary-priority keeps the BoM quantity; independent is not copied."""
        self.pallet.dependency_type = "secondary_priority"
        self.bag.dependency_type = "independent"
        production = self._new_production()
        self._assert_secondary(production, self.pallet, 1.0, 20.0)
        self.assertFalse(production.move_raw_ids.secondary_uom_id)

    def test_backorder_secondary_qty_follows_remaining_qty(self):
        production = self._new_production(product_qty=60.0)
        production.action_confirm()
        production.qty_producing = 20.0
        production.move_raw_ids.picked = True
        action = production.with_context(skip_consumption=True).button_mark_done()
        Form(
            self.env[action["res_model"]].with_context(**action["context"])
        ).save().action_backorder()
        backorder = production.procurement_group_id.mrp_production_ids - production
        self._assert_secondary(backorder, self.pallet, 2.0, 40.0)

    def test_split_secondary_qty_follows_split_qty(self):
        production = self._new_production(product_qty=60.0)
        production.action_confirm()
        action = production.action_split()
        split_form = Form(
            self.env["mrp.production.split"].with_context(**action["context"])
        )
        split_form.counter = 3
        split_form.save().action_split()
        productions = production.procurement_group_id.mrp_production_ids
        self.assertEqual(productions.mapped("product_qty"), [20.0] * 3)
        self.assertEqual(productions.mapped("secondary_uom_qty"), [1.0] * 3)

    def test_component_added_manually_without_bom_line(self):
        production = self._new_production()
        with Form(production) as production_form:
            with production_form.move_raw_ids.new() as move_form:
                move_form.product_id = self.byproduct
                move_form.product_uom_qty = 3.0
        move = production.move_raw_ids.filtered(
            lambda m: m.product_id == self.byproduct
        )
        self.assertFalse(move.secondary_uom_id)
