# Copyright 2018-19 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

from odoo.tests.common import SavepointCase


class TestMrpMultiLevelCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mo_obj = cls.env['mrp.production']
        cls.po_obj = cls.env['purchase.order']
        cls.product_obj = cls.env['product.product']
        cls.loc_obj = cls.env['stock.location']
        cls.mrp_area_obj = cls.env['mrp.area']
        cls.product_mrp_area_obj = cls.env['product.mrp.area']
        cls.partner_obj = cls.env['res.partner']
        cls.res_users = cls.env['res.users']
        cls.stock_picking_obj = cls.env['stock.picking']
        cls.mrp_multi_level_wiz = cls.env['mrp.multi.level']
        cls.mrp_inventory_procure_wiz = cls.env['mrp.inventory.procure']
        cls.mrp_inventory_obj = cls.env['mrp.inventory']
        cls.mrp_move_obj = cls.env['mrp.move']
        cls.planned_order_obj = cls.env['mrp.planned.order']

        cls.fp_1 = cls.env.ref('mrp_multi_level.product_product_fp_1')
        cls.fp_2 = cls.env.ref('mrp_multi_level.product_product_fp_2')
        cls.sf_1 = cls.env.ref('mrp_multi_level.product_product_sf_1')
        cls.sf_2 = cls.env.ref('mrp_multi_level.product_product_sf_2')
        cls.pp_1 = cls.env.ref('mrp_multi_level.product_product_pp_1')
        cls.pp_2 = cls.env.ref('mrp_multi_level.product_product_pp_2')
        cls.company = cls.env.ref('base.main_company')
        cls.mrp_area = cls.env.ref('mrp_multi_level.mrp_area_stock_wh0')
        cls.vendor = cls.env.ref('mrp_multi_level.res_partner_lazer_tech')
        cls.wh = cls.env.ref('stock.warehouse0')
        cls.stock_location = cls.wh.lot_stock_id
        cls.customer_location = cls.env.ref(
            'stock.stock_location_customers')
        cls.calendar = cls.env.ref('resource.resource_calendar_std')
        # Add calendar to WH:
        cls.wh.calendar_id = cls.calendar

        # Partner:
        vendor1 = cls.partner_obj.create({'name': 'Vendor 1'})

        # Create user:
        group_mrp_manager = cls.env.ref('mrp.group_mrp_manager')
        group_user = cls.env.ref('base.group_user')
        group_stock_manager = cls.env.ref('stock.group_stock_manager')
        cls.mrp_manager = cls._create_user(
            'Test User',
            [group_mrp_manager, group_user, group_stock_manager],
            cls.company,
        )

        # Create secondary location and MRP Area:
        cls.sec_loc = cls.loc_obj.create({
            'name': 'Test location',
            'usage': 'internal',
            'location_id': cls.wh.view_location_id.id,
        })
        cls.secondary_area = cls.mrp_area_obj.create({
            'name': 'Test',
            'warehouse_id': cls.wh.id,
            'location_id': cls.sec_loc.id,
        })

        # Create products:
        route_buy = cls.env.ref('purchase_stock.route_warehouse0_buy').id
        cls.prod_test = cls.product_obj.create({
            'name': 'Test Top Seller',
            'type': 'product',
            'list_price': 150.0,
            'produce_delay': 5.0,
            'route_ids': [(6, 0, [route_buy])],
            'seller_ids': [(0, 0, {'name': vendor1.id, 'price': 20.0})],
        })
        cls.product_mrp_area_obj.create({
            'product_id': cls.prod_test.id,
            'mrp_area_id': cls.mrp_area.id,
        })
        # Parameters in secondary area with nbr_days set.
        cls.product_mrp_area_obj.create({
            'product_id': cls.prod_test.id,
            'mrp_area_id': cls.secondary_area.id,
            'mrp_nbr_days': 7,
        })
        cls.prod_min = cls.product_obj.create({
            'name': 'Product with minimum order qty',
            'type': 'product',
            'list_price': 50.0,
            'route_ids': [(6, 0, [route_buy])],
            'seller_ids': [(0, 0, {'name': vendor1.id, 'price': 10.0})],
        })
        cls.product_mrp_area_obj.create({
            'product_id': cls.prod_min.id,
            'mrp_area_id': cls.mrp_area.id,
            'mrp_minimum_order_qty': 50.0,
            'mrp_maximum_order_qty': 0.0,
            'mrp_qty_multiple': 1.0,
        })

        cls.prod_max = cls.product_obj.create({
            'name': 'Product with maximum order qty',
            'type': 'product',
            'list_price': 50.0,
            'route_ids': [(6, 0, [route_buy])],
            'seller_ids': [(0, 0, {'name': vendor1.id, 'price': 10.0})],
        })
        cls.product_mrp_area_obj.create({
            'product_id': cls.prod_max.id,
            'mrp_area_id': cls.mrp_area.id,
            'mrp_minimum_order_qty': 50.0,
            'mrp_maximum_order_qty': 100.0,
            'mrp_qty_multiple': 1.0,
        })
        cls.prod_multiple = cls.product_obj.create({
            'name': 'Product with qty multiple',
            'type': 'product',
            'list_price': 50.0,
            'route_ids': [(6, 0, [route_buy])],
            'seller_ids': [(0, 0, {'name': vendor1.id, 'price': 10.0})],
        })
        cls.product_mrp_area_obj.create({
            'product_id': cls.prod_multiple.id,
            'mrp_area_id': cls.mrp_area.id,
            'mrp_minimum_order_qty': 50.0,
            'mrp_maximum_order_qty': 500.0,
            'mrp_qty_multiple': 25.0,
        })
        # Create test picking for FP-1 and FP-2:
        res = cls.calendar.plan_days(7 + 1, datetime.today().replace(hour=0))
        date_move = res.date()
        cls.picking_1 = cls.stock_picking_obj.create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.customer_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move fp-1',
                    'product_id': cls.fp_1.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.fp_1.uom_id.id,
                    'product_uom_qty': 100,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                }),
                (0, 0, {
                    'name': 'Test move fp-2',
                    'product_id': cls.fp_2.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.fp_2.uom_id.id,
                    'product_uom_qty': 15,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                })]
        })
        cls.picking_1.action_confirm()

        # Create test picking for procure qty adjustment tests:
        cls.picking_2 = cls.stock_picking_obj.create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.customer_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move prod_min',
                    'product_id': cls.prod_min.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.prod_min.uom_id.id,
                    'product_uom_qty': 16,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                }),
                (0, 0, {
                    'name': 'Test move prod_max',
                    'product_id': cls.prod_max.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.prod_max.uom_id.id,
                    'product_uom_qty': 140,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                }),
                (0, 0, {
                    'name': 'Test move prod_multiple',
                    'product_id': cls.prod_multiple.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.prod_multiple.uom_id.id,
                    'product_uom_qty': 112,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                })]
        })
        cls.picking_2.action_confirm()

        # Create Test PO:
        date_po = cls.calendar.plan_days(
            1+1, datetime.today().replace(hour=0)).date()
        cls.po = cls.po_obj.create({
            'name': 'Test PO-001',
            'partner_id': cls.vendor.id,
            'order_line': [
                (0, 0, {
                    'name': 'Test PP-2 line',
                    'product_id': cls.pp_2.id,
                    'date_planned': date_po,
                    'product_qty': 5.0,
                    'product_uom': cls.pp_2.uom_id.id,
                    'price_unit': 25.0,
                })],
        })

        # Create test MO:
        date_mo = cls.calendar.plan_days(
            9 + 1, datetime.today().replace(hour=0)).date()
        bom_fp_2 = cls.env.ref('mrp_multi_level.mrp_bom_fp_2')
        cls.mo = cls.mo_obj.create({
            'product_id': cls.fp_2.id,
            'bom_id': bom_fp_2.id,
            'product_qty': 12.0,
            'product_uom_id': cls.fp_2.uom_id.id,
            'date_planned_start': date_mo,
        })

        # Dates:
        today = datetime.today().replace(hour=0)
        cls.date_3 = cls.calendar.plan_days(3 + 1, today).date()
        cls.date_5 = cls.calendar.plan_days(5 + 1, today).date()
        cls.date_6 = cls.calendar.plan_days(6 + 1, today).date()
        cls.date_7 = cls.calendar.plan_days(7 + 1, today).date()
        cls.date_8 = cls.calendar.plan_days(8 + 1, today).date()
        cls.date_9 = cls.calendar.plan_days(9 + 1, today).date()
        cls.date_10 = cls.calendar.plan_days(10 + 1, today).date()
        cls.date_20 = cls.calendar.plan_days(20 + 1, today).date()
        cls.date_22 = cls.calendar.plan_days(22 + 1, today).date()

        # Create movements in secondary area:
        cls.create_demand_sec_loc(cls.date_8, 80.0)
        cls.create_demand_sec_loc(cls.date_9, 50.0)
        cls.create_demand_sec_loc(cls.date_10, 70.0)
        cls.create_demand_sec_loc(cls.date_20, 46.0)
        cls.create_demand_sec_loc(cls.date_22, 33.0)

        cls.mrp_multi_level_wiz.create({}).run_mrp_multi_level()

    @classmethod
    def create_demand_sec_loc(cls, date_move, qty):
        return cls.stock_picking_obj.create({
            "picking_type_id": cls.env.ref("stock.picking_type_out").id,
            "location_id": cls.sec_loc.id,
            "location_dest_id": cls.customer_location.id,
            "move_lines": [
                (0, 0, {
                    "name": "Test move",
                    "product_id": cls.prod_test.id,
                    "date_expected": date_move,
                    "date": date_move,
                    "product_uom": cls.prod_test.uom_id.id,
                    "product_uom_qty": qty,
                    "location_id": cls.sec_loc.id,
                    "location_dest_id": cls.customer_location.id,
                })],
        })

    @classmethod
    def _create_user(cls, login, groups, company):
        user = cls.res_users.create({
            'name': login,
            'login': login,
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': company.id,
            'groups_id': [(6, 0, [group.id for group in groups])]
        })
        return user
