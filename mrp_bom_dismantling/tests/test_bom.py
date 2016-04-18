# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import exceptions

from openerp.exceptions import UserError
from openerp.tests import TransactionCase


class TestBom(TransactionCase):

    def setUp(self):
        super(TestBom, self).setUp()

        self.product_model = self.env['product.product']
        self.bom_model = self.env['mrp.bom']
        self.bom_line_model = self.env['mrp.bom.line']
        self.mrp_production_model = self.env['mrp.production']
        self.config_param_model = self.env['ir.config_parameter']

        self.unit_uom = self.browse_ref('product.product_uom_unit')
        self.dozen_uom = self.browse_ref('product.product_uom_dozen')

    def check_result_and_load_entity(self, model_name, result, context=None):
        entity_id = result.pop('res_id')
        self.assertEqual({
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': model_name,
            'target': 'current',
            'context': context or self.env.context,
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

    def test_action_create_dismantling_bom(self):
        # Set component automatically choosen.
        self.config_param_model.set_param(
            'mrp.bom.dismantling.product_choice', False
        )

        p1 = self.product_model.create({'name': 'Test P1'})
        p2 = self.product_model.create({'name': 'Test P2'})

        p1_bom = self.create_bom(p1, components=[p2])

        dismantled_p2_domain = [
            ('product_id', '=', p2.id),
            ('dismantling', '=', True),
        ]

        # Non dismantling bom
        self.assertEqual(0, self.bom_model.search_count(dismantled_p2_domain))

        result = p1_bom.action_create_dismantling_bom()
        self.assertEqual(1, self.bom_model.search_count(dismantled_p2_domain))

        dmtl_bom = self.check_result_and_load_entity('mrp.bom', result)
        self.assertEqual(p2.id, dmtl_bom.product_id.id)
        self.assertEqual(True, dmtl_bom.dismantling)

        # Component must be choose by user
        self.config_param_model.set_param(
            'mrp.bom.dismantling.product_choice', '1'
        )

        result = p1_bom.action_create_dismantling_bom()

        # No new dismantling bom created
        self.assertEqual(1, self.bom_model.search_count(dismantled_p2_domain))

        # Response opened wizard
        self.assertEqual({
            'type': 'ir.actions.act_window',
            'name': 'Choose main compoment',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.bom.dismantling_product_choice',
            'target': 'new',
            'context': self.env.context
        }, result)

    def test_res_config(self):
        # Coverage test for res_config methods
        self.config_param_model.set_param(
            'mrp.bom.dismantling.product_choice', None
        )

        mrp_config = self.env['mrp.config.settings'].create({
            # Bypass default_get bug: https://github.com/odoo/odoo/pull/10373
            'group_product_variant': 0
        })
        self.assertEqual(
            False, mrp_config.read(
                ['dismantling_product_choice']
            )[0]['dismantling_product_choice']
        )

        mrp_config.write({'dismantling_product_choice': 1})
        mrp_config.execute()

        self.assertEqual('1', self.config_param_model.get_param(
            'mrp.bom.dismantling.product_choice'
        ))

    def test_product_choice_wizard(self):
        wizard_model = self.env['mrp.bom.dismantling_product_choice']

        p1 = self.product_model.create({'name': 'Test P1'})
        p2 = self.product_model.create({'name': 'Test P2'})
        p3 = self.product_model.create({'name': 'Test P3'})

        bom = self.create_bom(p1)

        # No active ID
        with self.assertRaises(KeyError):
            wizard_model.create({})

        # Cannot really test full workflow => call methods manually.
        wizard = wizard_model.with_context(active_id=bom.id).new({})
        self.assertEqual(bom, wizard._get_bom_id())

        wizard.bom_id = bom

        # No component
        with self.assertRaises(UserError):
            wizard.on_change_bom_id()

        self.create_bom_line(bom, p2)
        self.create_bom_line(bom, p3)

        bom.refresh()
        wizard.bom_id = bom
        result = wizard.on_change_bom_id()
        self.assertEqual({
            'domain': {
                'component_id': [('id', 'in', [p2.id, p3.id])],
            }
        }, result)

        wizard.component_id = p3
        wizard.write({})
        result = wizard.create_bom()

        # Dismantling BOM main product is P3
        dmtl_bom = self.check_result_and_load_entity(
            'mrp.bom', result, context={'active_id': bom.id}
        )
        self.assertEqual(p3.id, dmtl_bom.product_id.id)
        self.assertEqual(True, dmtl_bom.dismantling)
