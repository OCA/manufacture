# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpProductionHierarchy(TestMrpCommon):
    def setUp(self):
        super().setUp()
        self.bom_2.write({"type": "normal"})
        route_manufacture = self.env.ref("mrp.route_warehouse0_manufacture")
        route_mto = self.env.ref("stock.route_warehouse0_mto")
        (self.bom_1 | self.bom_2 | self.bom_3).mapped("product_id").write(
            {"route_ids": [(6, 0, [route_manufacture.id, route_mto.id])]}
        )

    def test_production_hierarchy(self):
        # bom_3 (product_6) -> bom_2 (product_5) -> bom_1 (product_4)
        production_form = Form(self.env["mrp.production"])
        production_form.product_id = self.product_6
        production_form.bom_id = self.bom_3
        production_form.product_qty = 2
        production_form.product_uom_id = self.product_6.uom_id
        man_order = production_form.save()

        man_order.action_confirm()
        self.assertEqual(len(man_order.child_ids), 2)
        self.assertIn(self.bom_2.product_id, man_order.child_ids.mapped("product_id"))
        for child in man_order.child_ids:
            self.assertIn(child.product_id, [self.product_5, self.product_4])
            self.assertEqual(child.root_id, man_order)
            self.assertEqual(child.parent_id, man_order)
            if child.product_id == self.bom_2.product_id:
                self.assertTrue(child.child_ids)
                self.assertTrue(child.open_production_tree())
            for child2 in child.child_ids:
                self.assertIn(child2.product_id, [self.product_4])
                self.assertEqual(child2.root_id, man_order)
                self.assertEqual(child2.parent_id, child)
        self.assertTrue(man_order.open_production_tree())
