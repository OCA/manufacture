# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import exceptions
from openerp.tests import TransactionCase


class TestBom(TransactionCase):

    def setUp(self):
        super(TestBom, self).setUp()

        self.product_model = self.env['product.product']
        self.bom_model = self.env['mrp.bom']
        self.bom_line_model = self.env['mrp.bom.line']
        self.mrp_production_model = self.env['mrp.production']

        self.unit_uom = self.browse_ref('product.product_uom_unit')
        self.dozen_uom = self.browse_ref('product.product_uom_dozen')

    def check_result_and_load_entity(self, model_name, result):
        entity_id = result.pop('res_id')
        self.assertEqual({
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': model_name,
            'target': 'current',
            'context': self.env.context
        }, result)

        return self.env[model_name].browse(entity_id)

    def create_bom(self, product, qty=1, uom=None,
                   phantom=False, components=None):
        bom = self.bom_model.create({
            'product_tmpl_id': product.product_tmpl_id.id,
            'product_id': product.id,
            'product_qty': qty,
            'product_uom': self.unit_uom.id if uom is None else uom.id,
            'type': 'phantom' if phantom else 'normal',
        })

        if components:
            for component in components:
                self.create_bom_line(bom, component)
        return bom

    def create_bom_line(self, bom, component, qty=1, uom=None):
        self.bom_line_model.create({
            'bom_id': bom.id,
            'product_id': component.id,
            'product_qty': qty,
            'product_uom': self.unit_uom.id if uom is None else uom.id,
        })

    def test_dismantling_no_components(self):
        p1 = self.product_model.create({'name': 'Test P1'})
        p2 = self.product_model.create({'name': 'Test P1'})

        p1_bom = self.create_bom(p1)

        with self.assertRaises(exceptions.UserError):
            p1_bom.create_dismantling_bom()

        self.create_bom_line(p1_bom, p2)
        p1_bom.create_dismantling_bom()

    def test_dismantling_on_dismantling_bom(self):
        p1 = self.product_model.create({'name': 'Test P1'})
        p2 = self.product_model.create({'name': 'Test P1'})

        p1_bom = self.create_bom(p1, components=[p2])
        p1_bom.write({
            'dismantling': True,
            'dismantled_product_id': p2.id
        })

        with self.assertRaises(exceptions.UserError):
            p1_bom.create_dismantling_bom()

    def test_dismantling_bom_no_product_id__multiple_vaiants(self):
        p1 = self.product_model.create({'name': 'Test P1'})
        p1_var = self.product_model.create({
            'product_tmpl_id': p1.product_tmpl_id.id,
        })
        p2 = self.product_model.create({'name': 'Test P2'})

        # P1 BoM: Need one P2
        p1_bom = self.bom_model.create({
            'product_tmpl_id': p1.product_tmpl_id.id,
            'product_id': None,
        })
        self.create_bom_line(p1_bom, p2)

        # No variant specified (and template has multiple variants)
        with self.assertRaises(exceptions.UserError):
            p1_bom.create_dismantling_bom()

        # Variant specified
        p1_bom.product_id = p1_var
        result = p1_bom.create_dismantling_bom()
        self.check_result_and_load_entity('mrp.bom', result)

    def test_dismantling_bom_no_product_id(self):
        # Same tests but BoM only have a product_tmpl_id, no product_id
        # (Seems to be the standard case)

        p1 = self.product_model.create({'name': 'Test P1'})
        p2 = self.product_model.create({'name': 'Test P2'})

        # P1 BoM: Need one P2
        p1_bom = self.bom_model.create({
            'product_tmpl_id': p1.product_tmpl_id.id,
            'product_id': None,
        })
        self.create_bom_line(p1_bom, p2)

        result = p1_bom.create_dismantling_bom()

        dmtl_bom = self.check_result_and_load_entity('mrp.bom', result)
        self.assertEqual(p2.id, dmtl_bom.product_id.id)
        self.assertEqual(True, dmtl_bom.dismantling)
        self.assertEqual(p1.id, dmtl_bom.dismantled_product_id.id)
        self.assertEqual(p2.product_tmpl_id.id, dmtl_bom.product_tmpl_id.id)

        # Consume p1
        self.assertEqual(1, len(dmtl_bom.bom_line_ids))
        self.assertEqual(p1.id, dmtl_bom.bom_line_ids[0].product_id.id)

    def test_dismantling_simple_case(self):
        p1 = self.product_model.create({'name': 'Test P1'})
        p2 = self.product_model.create({'name': 'Test P2'})
        p3 = self.product_model.create({'name': 'Test P3'})

        # P1 BoM: Need one P2 and one P3
        p1_bom = self.create_bom(p1, components=[p2, p3])

        result = p1_bom.create_dismantling_bom()

        dmtl_bom = self.check_result_and_load_entity('mrp.bom', result)
        self.assertEqual(p2.id, dmtl_bom.product_id.id)
        self.assertEqual(p2.product_tmpl_id.id, dmtl_bom.product_tmpl_id.id)
        self.assertEqual(True, dmtl_bom.dismantling)
        self.assertEqual(p1.id, dmtl_bom.dismantled_product_id.id)

        # Consume p1
        self.assertEqual(1, len(dmtl_bom.bom_line_ids))
        self.assertEqual(p1.id, dmtl_bom.bom_line_ids[0].product_id.id)

        # P3 in by-products
        self.assertEqual(1, len(dmtl_bom.sub_products))
        self.assertEqual(p3.id, dmtl_bom.sub_products[0].product_id.id)

    def test_phantom_bom(self):
        p1 = self.product_model.create({'name': 'Test P1'})
        p2 = self.product_model.create({'name': 'Test P2'})
        sub_p2 = self.product_model.create({'name': 'Test sub P2'})
        p3 = self.product_model.create({'name': 'Test P3'})
        sub_p3 = self.product_model.create({'name': 'Test sub P3'})

        # P1 BoM: Need one P2 and one P3
        # P2 has a phantom BoM which need one sub P2
        # P3 has a normal Bom which need one sub p3
        p1_bom = self.create_bom(p1, components=[p2, p3])
        self.create_bom(p2, phantom=True, components=[sub_p2])
        self.create_bom(p3, components=[sub_p3])

        result = p1_bom.create_dismantling_bom()

        dmtl_bom = self.check_result_and_load_entity('mrp.bom', result)
        self.assertEqual(sub_p2.id, dmtl_bom.product_id.id)
        self.assertEqual(sub_p2.product_tmpl_id.id,
                         dmtl_bom.product_tmpl_id.id)
        self.assertEqual(True, dmtl_bom.dismantling)
        self.assertEqual(p1.id, dmtl_bom.dismantled_product_id.id)

        # Consume p1self.assertEqual(1, len(dmtl_bom.bom_line_ids))
        self.assertEqual(p1.id, dmtl_bom.bom_line_ids[0].product_id.id)

        # Sub P3 in by-products
        self.assertEqual(1, len(dmtl_bom.sub_products))
        self.assertEqual(p3.id, dmtl_bom.sub_products[0].product_id.id)

    def test_multi_unit_components(self):
        p1 = self.product_model.create({'name': 'Test P1'})
        p2 = self.product_model.create({'name': 'Test P2'})
        p3 = self.product_model.create({'name': 'Test P3'})
        p4 = self.product_model.create({'name': 'Test P4'})

        # P1 BoM (produced 1 dozen): Needs 2 P2, 4 P3 and 2 dozen P4
        # P2 has a phantom BoM which need one Dozen of P3
        #
        # => Dismantling BoM:
        #       Product: P3 (produced 28 unit)
        #       Component: 1 dozen P1

        p1_bom = self.create_bom(p1, qty=1, uom=self.dozen_uom)
        self.create_bom_line(p1_bom, p2, qty=2)
        self.create_bom_line(p1_bom, p3, qty=4)
        self.create_bom_line(p1_bom, p4, qty=2, uom=self.dozen_uom)

        p2_bom = self.create_bom(p2, phantom=True)
        self.create_bom_line(p2_bom, p3, qty=1, uom=self.dozen_uom)

        result = p1_bom.create_dismantling_bom()

        dmtl_bom = self.check_result_and_load_entity('mrp.bom', result)
        self.assertEqual(p3.id, dmtl_bom.product_id.id)
        self.assertEqual(28, dmtl_bom.product_qty)
        self.assertEqual(self.unit_uom, dmtl_bom.product_uom)
        self.assertEqual(True, dmtl_bom.dismantling)
        self.assertEqual(p1.id, dmtl_bom.dismantled_product_id.id)

        # Consume 1 dozen p1
        self.assertEqual(1, len(dmtl_bom.bom_line_ids))

        dmtl_bom_line = dmtl_bom.bom_line_ids[0]
        self.assertEqual(p1.id, dmtl_bom_line.product_id.id)
        self.assertEqual(1, dmtl_bom_line.product_qty)
        self.assertEqual(self.dozen_uom, dmtl_bom_line.product_uom)

        # Byproducts
        self.assertEqual(1, len(dmtl_bom.sub_products))

        dmtl_sub_product = dmtl_bom.sub_products[0]
        self.assertEqual(p4.id, dmtl_sub_product.product_id.id)
        self.assertEqual(24, dmtl_sub_product.product_qty)
        self.assertEqual(self.unit_uom, dmtl_sub_product.product_uom)

    def test_create_mrp_production(self):
        p1 = self.product_model.create({'name': 'Test P1'})
        p2 = self.product_model.create({'name': 'Test P2'})
        bom = self.create_bom(p1, qty=2, uom=self.dozen_uom, components=[p2])

        self.assertEqual(
            0,
            self.mrp_production_model.search_count([('bom_id', '=', bom.id)])
        )

        result = bom.create_mrp_production()
        mrp_prod = self.check_result_and_load_entity('mrp.production', result)

        self.assertEqual(bom, mrp_prod.bom_id)
        self.assertEqual(p1, mrp_prod.product_id)
        self.assertEqual(2, mrp_prod.product_qty)
        self.assertEqual(2, mrp_prod.product_qty)
        self.assertEqual(self.dozen_uom, mrp_prod.product_uom)
