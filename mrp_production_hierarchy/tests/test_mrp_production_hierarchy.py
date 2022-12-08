# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpProductionHierarchy(TestMrpCommon):

    def setUp(self):
        super(TestMrpProductionHierarchy, self).setUp()
        self.bom_2.write({'type': 'normal'})
        route_manufacture = self.env.ref('mrp.route_warehouse0_manufacture')
        route_mto = self.env.ref('stock.route_warehouse0_mto')
        (self.bom_1 | self.bom_2 | self.bom_3).mapped('product_id').write(
            {'route_ids': [(6, 0, [route_manufacture.id, route_mto.id])]})

    def test_production_hierarchy(self):
        man_order = self.env['mrp.production'].create({
            'name': 'MO-Test',
            'product_id': self.product_6.id,
            'product_uom_id': self.product_6.uom_id.id,
            'product_qty': 2,
            'bom_id': self.bom_3.id,
        })
        self.assertEqual(len(man_order.child_ids), 2)
        for child in man_order.child_ids:
            self.assertIn(child.product_id, [self.product_5, self.product_4])
            self.assertEqual(child.root_id, man_order)
            self.assertEqual(child.parent_id, man_order)
            for child2 in child.child_ids:
                self.assertIn(child2.product_id, [self.product_4])
                self.assertEqual(child2.root_id, man_order)
                self.assertEqual(child2.parent_id, child)
