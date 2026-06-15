# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMrpBomComponentMassChange(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.MrpBom = cls.env["mrp.bom"]
        cls.Wizard = cls.env["mrp.bom.component.mass.change"]
        # Existing instances
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        # Instances
        cls.component = cls._create_product("Component A")
        cls.new_component = cls._create_product("Component B")
        cls.new_component_kg = cls._create_product("Component C", uom=cls.uom_kg)
        cls.other_component = cls._create_product("Other Component")
        cls.bom_1 = cls._create_bom(
            cls._create_product("Finished 1"),
            [(cls.component, 2.0), (cls.other_component, 1.0)],
        )
        cls.bom_2 = cls._create_bom(
            cls._create_product("Finished 2"), [(cls.component, 5.0)]
        )
        cls.bom_3 = cls._create_bom(
            cls._create_product("Finished 3"), [(cls.other_component, 3.0)]
        )

    @classmethod
    def _create_product(cls, name, uom=None, **kwargs):
        vals = {"name": name}
        if uom is not None:
            vals.update({"uom_id": uom.id, "uom_po_id": uom.id})
        vals.update(kwargs)
        return cls.env["product.product"].create(vals)

    @classmethod
    def _create_bom(cls, product, components, **kwargs):
        vals = {
            "product_tmpl_id": product.product_tmpl_id.id,
            "product_qty": 1.0,
            "bom_line_ids": [
                (0, 0, {"product_id": component.id, "product_qty": qty})
                for component, qty in components
            ],
        }
        vals.update(kwargs)
        return cls.MrpBom.create(vals)

    def _component_lines(self, bom, product):
        return bom.bom_line_ids.filtered(lambda line: line.product_id == product)

    def test_compute_bom_ids(self):
        wizard = self.Wizard.create({"component_id": self.component.id})
        self.assertEqual(wizard.bom_ids, self.bom_1 | self.bom_2)

    def test_default_get_from_bom_line(self):
        line = self._component_lines(self.bom_1, self.component)
        wizard = self.Wizard.with_context(
            active_model="mrp.bom.line", active_ids=line.ids
        ).create({})
        self.assertEqual(wizard.component_id, self.component)
        self.assertEqual(wizard.bom_ids, self.bom_1 | self.bom_2)

    def test_bom_line_action(self):
        line = self._component_lines(self.bom_2, self.component)
        action = line.action_bom_component_mass_change()
        self.assertEqual(action["res_model"], "mrp.bom.component.mass.change")
        self.assertEqual(action["context"]["default_component_id"], self.component.id)
        self.assertTrue(action["context"]["default_component_locked"])

    def test_component_in_multiple_boms(self):
        line = self._component_lines(self.bom_1, self.component)
        self.assertTrue(line.component_in_multiple_boms)
        single_component = self._create_product("Single Component")
        single_bom = self._create_bom(
            self._create_product("Finished 4"), [(single_component, 1.0)]
        )
        single_line = self._component_lines(single_bom, single_component)
        self.assertFalse(single_line.component_in_multiple_boms)

    def test_replace_component(self):
        wizard = self.Wizard.create(
            {
                "component_id": self.component.id,
                "change_type": "replace",
                "new_component_id": self.new_component.id,
                "new_product_qty": 7.0,
            }
        )
        wizard.action_apply()
        line_1 = self._component_lines(self.bom_1, self.new_component)
        line_2 = self._component_lines(self.bom_2, self.new_component)
        self.assertEqual(len(line_1), 1)
        self.assertEqual(len(line_2), 1)
        self.assertEqual(line_1.product_qty, 7.0)
        self.assertEqual(line_2.product_qty, 7.0)
        self.assertEqual(line_1.product_uom_id, self.uom_unit)
        self.assertFalse(self._component_lines(self.bom_1, self.component))
        self.assertFalse(self._component_lines(self.bom_2, self.component))
        self.assertEqual(
            len(self._component_lines(self.bom_1, self.other_component)), 1
        )

    def test_replace_component_different_uom_category(self):
        wizard = self.Wizard.create(
            {
                "component_id": self.component.id,
                "change_type": "replace",
                "new_component_id": self.new_component_kg.id,
                "new_product_qty": 4.0,
            }
        )
        wizard.action_apply()
        line = self._component_lines(self.bom_1, self.new_component_kg)
        self.assertEqual(line.product_uom_id, self.uom_kg)
        self.assertEqual(line.product_qty, 4.0)

    def test_remove_component_selected_boms_only(self):
        wizard = self.Wizard.create(
            {
                "component_id": self.component.id,
                "change_type": "remove",
            }
        )
        wizard.bom_ids = self.bom_1
        wizard.action_apply()
        self.assertFalse(self._component_lines(self.bom_1, self.component))
        self.assertEqual(len(self._component_lines(self.bom_2, self.component)), 1)
        self.assertEqual(
            len(self._component_lines(self.bom_1, self.other_component)), 1
        )

    def test_no_bom_selected(self):
        wizard = self.Wizard.create(
            {
                "component_id": self.component.id,
                "change_type": "remove",
            }
        )
        wizard.bom_ids = False
        with self.assertRaisesRegex(UserError, "at least one bill of materials"):
            wizard.action_apply()

    def test_replace_without_new_component(self):
        wizard = self.Wizard.create(
            {
                "component_id": self.component.id,
                "change_type": "replace",
            }
        )
        with self.assertRaisesRegex(UserError, "select the new component"):
            wizard.action_apply()

    def test_replace_with_same_component(self):
        wizard = self.Wizard.create(
            {
                "component_id": self.component.id,
                "change_type": "replace",
                "new_component_id": self.component.id,
            }
        )
        with self.assertRaisesRegex(UserError, "must be different"):
            wizard.action_apply()
