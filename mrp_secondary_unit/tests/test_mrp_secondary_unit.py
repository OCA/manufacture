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
        # Secondary units are only shown, and therefore only round-tripped by
        # the form views, to users managing units of measure.
        cls.env.user.groups_id |= cls.env.ref("uom.group_uom") | cls.env.ref(
            "mrp.group_mrp_byproducts"
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.finished = cls.env["product.product"].create(
            {
                "name": "Test finished product",
                "is_storable": True,
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_unit.id,
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "name": "Pallet of 20",
                            "uom_id": cls.uom_unit.id,
                            "factor": 20.0,
                        }
                    )
                ],
            }
        )
        cls.finished_pallet = cls.finished.product_tmpl_id.secondary_uom_ids
        cls.component = cls.env["product.product"].create(
            {
                "name": "Test component",
                "is_storable": True,
                "uom_id": cls.uom_kg.id,
                "uom_po_id": cls.uom_kg.id,
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "name": "Bag of 5 kg",
                            "uom_id": cls.uom_unit.id,
                            "factor": 5.0,
                        }
                    )
                ],
            }
        )
        cls.component_bag = cls.component.product_tmpl_id.secondary_uom_ids
        cls.byproduct = cls.env["product.product"].create(
            {
                "name": "Test byproduct",
                "is_storable": True,
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_unit.id,
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "name": "Crate of 4",
                            "uom_id": cls.uom_unit.id,
                            "factor": 4.0,
                        }
                    )
                ],
            }
        )
        cls.byproduct_crate = cls.byproduct.product_tmpl_id.secondary_uom_ids
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished.product_tmpl_id.id,
                "product_uom_id": cls.uom_unit.id,
                "secondary_uom_id": cls.finished_pallet.id,
                "secondary_uom_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.component.id,
                            "product_uom_id": cls.uom_kg.id,
                            "secondary_uom_id": cls.component_bag.id,
                            "secondary_uom_qty": 2.0,
                        }
                    )
                ],
                "byproduct_ids": [
                    Command.create(
                        {
                            "product_id": cls.byproduct.id,
                            "product_uom_id": cls.uom_unit.id,
                            "secondary_uom_id": cls.byproduct_crate.id,
                            "secondary_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )

    def _new_production(self, product_qty=None):
        production_form = Form(self.env["mrp.production"])
        production_form.product_id = self.finished
        production_form.bom_id = self.bom
        if product_qty is not None:
            production_form.product_qty = product_qty
        return production_form.save()

    def test_bom_secondary_qty_drives_product_qty(self):
        """The recipe is written in the secondary unit and stored in the
        primary one."""
        self.assertEqual(self.bom.product_qty, 20.0)
        self.assertEqual(self.bom.bom_line_ids.product_qty, 10.0)
        self.assertEqual(self.bom.byproduct_ids.product_qty, 4.0)

    def test_bom_secondary_qty_change(self):
        self.bom.bom_line_ids.secondary_uom_qty = 3.0
        self.assertEqual(self.bom.bom_line_ids.product_qty, 15.0)

    def test_bom_uom_differs_from_product_uom(self):
        """The factor refers to the UoM of the product, not to the one of the
        line, so a line encoded in grams is converted first."""
        self.bom.bom_line_ids.product_uom_id = self.uom_gram
        self.bom.bom_line_ids.secondary_uom_qty = 1.0
        # 1 bag of 5 kg -> 5 kg -> 5000 g
        self.assertEqual(self.bom.bom_line_ids.product_qty, 5000.0)

    def test_bom_defined_on_template(self):
        """A bill of materials without a variant falls back on the template to
        resolve the UoM the factor refers to."""
        self.assertFalse(self.bom.product_id)
        self.bom.product_uom_id = self.uom_dozen
        self.bom.secondary_uom_qty = 1.0
        # 1 pallet of 20 units -> 20 units -> 20/12 dozens
        self.assertAlmostEqual(self.bom.product_qty, 20.0 / 12.0, places=2)

    def test_production_secondary_unit_from_bom(self):
        production = self._new_production()
        self.assertEqual(production.secondary_uom_id, self.finished_pallet)
        self.assertEqual(production.product_qty, 20.0)
        self.assertEqual(production.secondary_uom_qty, 1.0)

    def test_production_secondary_unit_picked_keeps_qty_to_produce(self):
        """Picking a secondary unit derives the secondary quantity from the
        quantity to produce; it must not reset that quantity."""
        with Form(self.env["mrp.production"]) as production_form:
            production_form.product_id = self.finished
            production_form.bom_id = self.bom
            production_form.secondary_uom_id = self.env["product.secondary.unit"]
            self.assertEqual(production_form.product_qty, 20.0)
            production_form.secondary_uom_id = self.finished_pallet
            self.assertEqual(production_form.product_qty, 20.0)
            self.assertEqual(production_form.secondary_uom_qty, 1.0)

    def _view_secondary_uom_domain(self, model, view_xmlid, values):
        """Evaluate the domain the form view puts on the header secondary unit.

        The header is the only ``secondary_uom_id`` of these forms that is not
        inside an embedded list.
        """
        arch = etree.fromstring(
            self.env[model].get_view(self.env.ref(view_xmlid).id)["arch"]
        )
        nodes = arch.xpath("//field[@name='secondary_uom_id'][not(ancestor::list)]")
        self.assertEqual(len(nodes), 1)
        return safe_eval(nodes[0].get("domain"), dict(values))

    def test_bom_secondary_unit_domain_offers_units_of_the_template(self):
        """A unit defined on the variant form carries ``product_id``, so a bill
        of materials without a variant has to match on the template alone or
        its list of units comes out empty."""
        self.assertFalse(self.bom.product_id)
        self.assertTrue(self.finished_pallet.product_id)
        domain = self._view_secondary_uom_domain(
            "mrp.bom",
            "mrp.mrp_bom_form_view",
            {
                "product_tmpl_id": self.bom.product_tmpl_id.id,
                "product_id": self.bom.product_id.id,
            },
        )
        self.assertIn(
            self.finished_pallet, self.env["product.secondary.unit"].search(domain)
        )

    def test_production_secondary_unit_domain_offers_units_of_the_product(self):
        production = self._new_production()
        domain = self._view_secondary_uom_domain(
            "mrp.production",
            "mrp.mrp_production_form_view",
            {"product_id": production.product_id.id},
        )
        self.assertIn(
            self.finished_pallet, self.env["product.secondary.unit"].search(domain)
        )

    def test_bom_secondary_unit_picked_keeps_qty(self):
        """Same on a bill of materials, where a quantity reset to zero would
        also break the constraint keeping it positive."""
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished.product_tmpl_id.id,
                "product_uom_id": self.uom_unit.id,
                "product_qty": 10.0,
                "type": "normal",
            }
        )
        bom.secondary_uom_id = self.finished_pallet
        self.assertEqual(bom.product_qty, 10.0)
        self.assertEqual(bom.secondary_uom_qty, 0.5)

    def test_bom_line_secondary_unit_picked_keeps_qty(self):
        line = self.bom.bom_line_ids
        line.secondary_uom_id = self.env["product.secondary.unit"]
        line.product_qty = 10.0
        line.secondary_uom_id = self.component_bag
        self.assertEqual(line.product_qty, 10.0)
        self.assertEqual(line.secondary_uom_qty, 2.0)

    def test_production_secondary_qty_drives_product_qty(self):
        production = self._new_production()
        production.secondary_uom_qty = 3.0
        self.assertEqual(production.product_qty, 60.0)

    def test_component_secondary_values_from_bom(self):
        """The component of the order comes already expressed in the unit of
        the recipe, with the quantity derived from the exploded quantity."""
        production = self._new_production()
        move = production.move_raw_ids
        self.assertEqual(move.secondary_uom_id, self.component_bag)
        self.assertEqual(move.product_uom_qty, 10.0)
        self.assertEqual(move.secondary_uom_qty, 2.0)

    def test_component_secondary_qty_rescales_with_production_qty(self):
        production = self._new_production()
        production.product_qty = 60.0
        move = production.move_raw_ids
        self.assertEqual(move.product_uom_qty, 30.0)
        self.assertEqual(move.secondary_uom_qty, 6.0)

    def test_component_secondary_qty_rescales_on_qty_change_in_form(self):
        """The quantity exploded from the bill of materials must not be
        overwritten by the secondary quantity the move still carries from the
        previous quantity to produce."""
        with Form(self.env["mrp.production"]) as production_form:
            production_form.product_id = self.finished
            production_form.bom_id = self.bom
            production_form.product_qty = 60.0
        production = production_form.record
        move = production.move_raw_ids
        self.assertEqual(move.product_uom_qty, 30.0)
        self.assertEqual(move.secondary_uom_qty, 6.0)

    def test_byproduct_secondary_qty_rescales_on_qty_change_in_form(self):
        with Form(self.env["mrp.production"]) as production_form:
            production_form.product_id = self.finished
            production_form.bom_id = self.bom
            production_form.product_qty = 60.0
        production = production_form.record
        move = production.move_byproduct_ids
        self.assertEqual(move.product_uom_qty, 12.0)
        self.assertEqual(move.secondary_uom_qty, 3.0)

    def test_component_secondary_qty_drives_qty_to_consume(self):
        production = self._new_production()
        move = production.move_raw_ids
        move.secondary_uom_qty = 5.0
        self.assertEqual(move.product_uom_qty, 25.0)

    def test_byproduct_secondary_values_from_bom(self):
        production = self._new_production()
        move = production.move_byproduct_ids
        self.assertEqual(move.secondary_uom_id, self.byproduct_crate)
        self.assertEqual(move.product_uom_qty, 4.0)
        self.assertEqual(move.secondary_uom_qty, 1.0)

    def test_finished_move_secondary_unit(self):
        production = self._new_production()
        finished_move = production.move_finished_ids.filtered(
            lambda m: m.product_id == self.finished
        )
        self.assertEqual(finished_move.secondary_uom_id, self.finished_pallet)
        self.assertEqual(finished_move.secondary_uom_qty, 1.0)

    def test_component_added_manually_without_bom_line(self):
        """A component that does not come from the bill of materials must not
        break the propagation."""
        production = self._new_production()
        with Form(production) as production_form:
            with production_form.move_raw_ids.new() as move_form:
                move_form.product_id = self.byproduct
                move_form.product_uom_qty = 3.0
        move = production.move_raw_ids.filtered(
            lambda m: m.product_id == self.byproduct
        )
        self.assertFalse(move.secondary_uom_id)
