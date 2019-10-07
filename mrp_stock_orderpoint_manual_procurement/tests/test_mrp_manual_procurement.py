# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMrpManualProcurement(TransactionCase):

    def setUp(self):
        super(TestMrpManualProcurement, self).setUp()

        self.production_model = self.env['mrp.production']
        self.product_model = self.env['product.product']
        self.orderpoint_model = self.env['stock.warehouse.orderpoint']
        self.loc_model = self.env['stock.location']
        self.route_model = self.env['stock.location.route']
        self.manual_procurement_wiz = self.env['make.procurement.orderpoint']
        self.bom_model = self.env['mrp.bom']
        self.boml_model = self.env['mrp.bom.line']

        self.warehouse = self.env.ref('stock.warehouse0')
        self.stock_loc = self.env.ref('stock.stock_location_stock')
        route_manuf = self.env.ref('mrp.route_warehouse0_manufacture')

        # Create a new location and route:
        self.secondary_loc = self.loc_model.create({
            'name': 'Test location',
            'usage': 'internal',
            'location_id': self.warehouse.view_location_id.id,
        })
        test_route = self.route_model.create({
            'name': 'Stock -> Test',
            'product_selectable': True,
            'rule_ids': [(0, 0, {
                'name': 'stock to test',
                'action': 'pull',
                'location_id': self.secondary_loc.id,
                'location_src_id': self.stock_loc.id,
                'procure_method': 'make_to_order',
                'picking_type_id': self.env.ref(
                    'stock.picking_type_internal').id,
                'propagate': True
            })]
        })

        # Prepare Products:
        routes = route_manuf + test_route
        self.product = self.product_model.create({
            'name': 'Test Product',
            'route_ids': [(6, 0, routes.ids)],
        })
        component = self.product_model.create({
            'name': 'Test component',
        })

        # Create Bill of Materials:
        self.bom_1 = self.bom_model.create({
            'product_id': self.product.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'product_uom_id': self.product.uom_id.id,
            'product_qty': 1.0,
        })
        self.boml_model.create({
            'bom_id': self.bom_1.id,
            'product_id': component.id,
            'product_qty': 1.0,
        })

        # Create Orderpoint:
        self.orderpoint_stock = self.orderpoint_model.create({
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'product_id': self.product.id,
            'product_min_qty': 10.0,
            'product_max_qty': 50.0,
            'product_uom': self.product.uom_id.id,
        })
        self.orderpoint_secondary_loc = self.orderpoint_model.create({
            'warehouse_id': self.warehouse.id,
            'location_id': self.secondary_loc.id,
            'product_id': self.product.id,
            'product_min_qty': 10.0,
            'product_max_qty': 20.0,
            'product_uom': self.product.uom_id.id,
        })

        # Create User:
        self.test_user = self.env['res.users'].create({
            'name': 'John',
            'login': 'test',
        })

    def manual_procurement(self, orderpoint, user):
        """Make Procurement from Reordering Rule"""
        context = {
            'active_model': 'stock.warehouse.orderpoint',
            'active_ids': orderpoint.ids,
            'active_id': orderpoint.id
        }
        wizard = self.manual_procurement_wiz.sudo(user).\
            with_context(context).create({})
        wizard.make_procurement()
        return wizard

    def test_01_manual_procurement_requested_by(self):
        """Tests manual procurement fills requested_by field.
        Direct MO creation."""
        self.manual_procurement(self.orderpoint_stock, self.test_user)
        mo = self.production_model.search([
            ('requested_by', '=', self.test_user.id)])
        self.assertTrue(mo)
        self.assertEqual(mo.product_id, self.product)
        self.assertEqual(mo.product_qty, 50.0)

    def test_02_manual_procurement_requested_by_indirect(self):
        """Tests manual procurement fills requested_by field.
        Indirect MO creation (transfer -> MO)."""
        self.manual_procurement(self.orderpoint_secondary_loc, self.test_user)
        mo = self.production_model.search([
            ('requested_by', '=', self.test_user.id)])
        self.assertTrue(mo)
        self.assertEqual(mo.product_id, self.product)
        self.assertEqual(mo.product_qty, 20.0)
