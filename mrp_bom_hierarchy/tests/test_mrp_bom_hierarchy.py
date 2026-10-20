# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestBomHierarchy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.bom_obj = cls.env["mrp.bom"]
        cls.bom_line_obj = cls.env["mrp.bom.line"]

        # parent product A, child product B
        cls.product_a = cls.env["product.product"].create(
            {"name": "TEST A", "type": "consu"}
        )
        cls.product_b = cls.env["product.product"].create(
            {"name": "TEST B", "type": "consu"}
        )

        # bom_a: parent BoM (A = 1 B)
        cls.bom_a = cls.bom_obj.create(
            {"product_tmpl_id": cls.product_a.product_tmpl_id.id}
        )
        cls.bom_line_obj.create(
            {
                "product_id": cls.product_b.id,
                "bom_id": cls.bom_a.id,
                "product_qty": 1.0,
            }
        )
        # bom_b: child BoM for B
        cls.bom_b = cls.bom_obj.create(
            {"product_tmpl_id": cls.product_b.product_tmpl_id.id}
        )

    def test_01_computed_fields(self):
        self.assertTrue(self.bom_a.has_child)
        self.assertFalse(self.bom_a.has_parent)
        self.assertEqual(self.bom_a.child_bom_ids, self.bom_b)
        self.assertFalse(self.bom_a.parent_bom_ids)

        self.assertTrue(self.bom_b.has_parent)
        self.assertFalse(self.bom_b.has_child)
        self.assertEqual(self.bom_b.parent_bom_ids, self.bom_a)
        self.assertFalse(self.bom_b.child_bom_ids)

    def test_02_search_has_child(self):
        res = self.bom_obj.search([("has_child", "=", True)])
        self.assertEqual(res, self.bom_a)
        res = self.bom_obj.search([("has_child", "!=", True)])
        self.assertIn(self.bom_b, res)
        res = self.bom_obj.search([("has_child", "=", "False")])
        self.assertIn(self.bom_b, res)

    def test_03_search_has_parent(self):
        res = self.bom_obj.search([("has_parent", "=", True)])
        self.assertEqual(res, self.bom_b)
        res = self.bom_obj.search([("has_parent", "=", "True")])
        self.assertEqual(res, self.bom_b)

    def test_04_product_has_other_bom(self):
        self.assertFalse(self.bom_a.product_has_other_bom)
        # a second BoM for product A (without lines)
        bom_a2 = self.bom_obj.create(
            {"product_tmpl_id": self.product_a.product_tmpl_id.id}
        )
        # The compute of `product_has_other_bom` cannot depend on the other
        # BoMs of the same product (upstream limitation), so its cached value
        # is stale within the same transaction. Force a recompute.
        self.bom_a.invalidate_recordset(["product_has_other_bom"])
        self.assertTrue(self.bom_a.product_has_other_bom)
        self.assertTrue(bom_a2.product_has_other_bom)

    def test_05_bom_line_find(self):
        line = self.bom_line_obj._bom_line_find(product=self.product_b)
        self.assertEqual(line.bom_id, self.bom_a)
        # product without any BoM line
        product_c = self.env["product.product"].create(
            {"name": "TEST C", "type": "consu"}
        )
        self.assertFalse(self.bom_line_obj._bom_line_find(product=product_c))
        # service products are ignored
        product_d = self.env["product.product"].create(
            {"name": "TEST D", "type": "service"}
        )
        self.assertFalse(self.bom_line_obj._bom_line_find(product=product_d))

    def test_06_has_bom(self):
        # line_b points to bom_b
        line_b = self.bom_line_obj.search([("product_id", "=", self.product_b.id)])
        self.assertTrue(line_b.has_bom)
        # a line for a product without any BoM
        product_e = self.env["product.product"].create(
            {"name": "TEST E", "type": "consu"}
        )
        self.bom_line_obj.create(
            {
                "product_id": product_e.id,
                "bom_id": self.bom_a.id,
                "product_qty": 1.0,
            }
        )
        line_e = self.bom_line_obj.search([("product_id", "=", product_e.id)])
        self.assertFalse(line_e.has_bom)

    def test_07_action_buttons(self):
        # bom line with one child BoM -> form view on it
        line_b = self.bom_line_obj.search([("product_id", "=", self.product_b.id)])
        res = line_b.action_open_product_bom_tree_view()
        self.assertEqual(res["res_id"], self.bom_b.id)
        self.assertEqual(res["views"], [(False, "form")])

        # bom_a has children -> domain on child BoMs
        res = self.bom_a.action_open_child_tree_view()
        self.assertEqual(res["res_model"], "mrp.bom")
        self.assertEqual(res["domain"], f"[('id', 'in', [{self.bom_b.id}])]")
        self.assertEqual(
            res["context"], {"default_bom_line_ids": self.bom_a.bom_line_ids.ids}
        )

        # bom_b has no children -> no domain (mrp.mrp_bom_form_action sets
        # an empty domain in 19.0, so check the empty value instead of
        # absence)
        res = self.bom_b.action_open_child_tree_view()
        self.assertEqual(res.get("domain"), "[]")

        # bom_b has a parent -> domain on parent BoMs
        res = self.bom_b.action_open_parent_tree_view()
        self.assertEqual(res["domain"], f"[('id', 'in', [{self.bom_a.id}])]")

        # bom_a has no parent -> no domain
        res = self.bom_a.action_open_parent_tree_view()
        self.assertEqual(res.get("domain"), "[]")

        # product_b has another BoM -> domain on the other BoMs
        bom_b2 = self.bom_obj.create(
            {"product_tmpl_id": self.product_b.product_tmpl_id.id}
        )
        res = self.bom_b.action_open_product_other_bom_tree_view()
        self.assertEqual(res["domain"], f"[('id', 'in', [{bom_b2.id}])]")
        self.assertEqual(
            res["context"],
            {"default_product_tmpl_id": self.product_b.product_tmpl_id.id},
        )

        # product_a has no other BoM -> domain is an empty id list
        # (unlike child/parent actions, domain is always set here)
        res = self.bom_a.action_open_product_other_bom_tree_view()
        self.assertEqual(res["domain"], "[('id', 'in', [])]")
