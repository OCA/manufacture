# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpMultiLevelCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mo_obj = cls.env["mrp.production"]
        cls.po_obj = cls.env["purchase.order"]
        cls.product_obj = cls.env["product.product"]
        cls.loc_obj = cls.env["stock.location"]
        cls.quant_obj = cls.env["stock.quant"]
        cls.mrp_area_obj = cls.env["mrp.area"]
        cls.product_mrp_area_obj = cls.env["product.mrp.area"]
        cls.partner_obj = cls.env["res.partner"]
        cls.res_users = cls.env["res.users"]
        cls.stock_picking_obj = cls.env["stock.picking"]
        cls.mrp_multi_level_wiz = cls.env["mrp.multi.level"]
        cls.mrp_inventory_procure_wiz = cls.env["mrp.inventory.procure"]
        cls.mrp_inventory_obj = cls.env["mrp.inventory"]
        cls.mrp_move_obj = cls.env["mrp.move"]
        cls.planned_order_obj = cls.env["mrp.planned.order"]
        cls.lot_obj = cls.env["stock.lot"]
        cls.mrp_bom_obj = cls.env["mrp.bom"]

        cls._create_demo_data()

        cls.fp_1 = cls.env["product.product"].search([("name", "=", "FP-1")], limit=1)
        cls.fp_2 = cls.env["product.product"].search([("name", "=", "FP-2")], limit=1)
        cls.fp_3 = cls.env["product.product"].search([("name", "=", "FP-3")], limit=1)
        cls.fp_4 = cls.env["product.product"].search([("name", "=", "FP-4")], limit=1)
        cls.sf_1 = cls.env["product.product"].search([("name", "=", "SF-1")], limit=1)
        cls.sf_2 = cls.env["product.product"].search([("name", "=", "SF-2")], limit=1)
        cls.sf_3 = cls.env["product.product"].search([("name", "=", "SF-3")], limit=1)
        cls.pp_1 = cls.env["product.product"].search([("name", "=", "PP-1")], limit=1)
        cls.pp_2 = cls.env["product.product"].search([("name", "=", "PP-2")], limit=1)
        cls.pp_3 = cls.env["product.product"].search([("name", "=", "PP-3")], limit=1)
        cls.pp_4 = cls.env["product.product"].search([("name", "=", "PP-4")], limit=1)
        cls.product_4b = cls.env["product.product"].search(
            [("default_code", "=", "product.product_product_4b")], limit=1
        )
        cls.product_4c = cls.env["product.product"].search(
            [("default_code", "=", "product.product_product_4c")], limit=1
        )
        cls.av_11 = cls.env["product.product"].search(
            [("name", "=", "AV-11 steel")], limit=1
        )
        cls.av_12 = cls.env["product.product"].search(
            [("name", "=", "AV-12 aluminium")], limit=1
        )
        cls.av_21 = cls.env["product.product"].search(
            [("name", "=", "AV-21 white")], limit=1
        )
        cls.av_22 = cls.env["product.product"].search(
            [("name", "=", "AV-22 black")], limit=1
        )
        cls.company = cls.env.ref("base.main_company")
        cls.mrp_area = cls.mrp_area_obj.search([("name", "=", "Test Area")], limit=1)
        cls.vendor = cls.env["res.partner"].search(
            [("name", "=", "Lazer Tech")], limit=1
        )
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.wh.lot_stock_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.calendar = cls.env.ref("resource.resource_calendar_std")
        # Add calendar to WH:
        cls.wh.calendar_id = cls.calendar

        # Partner:
        vendor1 = cls.partner_obj.create({"name": "Vendor 1"})

        # Create user:
        group_mrp_manager = cls.env.ref("mrp.group_mrp_manager")
        group_user = cls.env.ref("base.group_user")
        group_stock_manager = cls.env.ref("stock.group_stock_manager")
        group_product_manager = cls.env.ref("product.group_product_manager")
        cls.mrp_manager = cls._create_user(
            "Test User",
            [group_mrp_manager, group_user, group_stock_manager, group_product_manager],
            cls.company,
        )

        # Create secondary location and MRP Area:
        cls.sec_loc = cls.loc_obj.create(
            {
                "name": "Test location",
                "usage": "internal",
                "location_id": cls.wh.view_location_id.id,
            }
        )
        cls.secondary_area = cls.mrp_area_obj.create(
            {"name": "Test", "warehouse_id": cls.wh.id, "location_id": cls.sec_loc.id}
        )
        # Create an area for design special cases and test them, different
        # cases will be expected to not share products, this way each case
        # can be isolated.
        cls.cases_loc = cls.loc_obj.create(
            {
                "name": "Special Cases location",
                "usage": "internal",
                "location_id": cls.wh.view_location_id.id,
            }
        )
        cls.cases_area = cls.mrp_area_obj.create(
            {
                "name": "Special Cases Tests",
                "warehouse_id": cls.wh.id,
                "location_id": cls.cases_loc.id,
            }
        )

        # Create products:
        route_buy = cls.env.ref("purchase_stock.route_warehouse0_buy").id
        cls.prod_test = cls.product_obj.create(
            {
                "name": "Test Top Seller",
                "is_storable": True,
                "list_price": 150.0,
                "route_ids": [(6, 0, [route_buy])],
                "seller_ids": [(0, 0, {"partner_id": vendor1.id, "price": 20.0})],
            }
        )
        cls.product_mrp_area_obj.create(
            {"product_id": cls.prod_test.id, "mrp_area_id": cls.mrp_area.id}
        )
        # Parameters in secondary area with nbr_days set.
        cls.product_mrp_area_obj.create(
            {
                "product_id": cls.prod_test.id,
                "mrp_area_id": cls.secondary_area.id,
                "mrp_nbr_days": 7,
            }
        )
        cls.prod_min = cls.product_obj.create(
            {
                "name": "Product with minimum order qty",
                "is_storable": True,
                "list_price": 50.0,
                "route_ids": [(6, 0, [route_buy])],
                "seller_ids": [(0, 0, {"partner_id": vendor1.id, "price": 10.0})],
            }
        )
        cls.product_mrp_area_obj.create(
            {
                "product_id": cls.prod_min.id,
                "mrp_area_id": cls.mrp_area.id,
                "mrp_minimum_order_qty": 50.0,
                "mrp_maximum_order_qty": 0.0,
                "mrp_qty_multiple": 1.0,
            }
        )

        cls.prod_max = cls.product_obj.create(
            {
                "name": "Product with maximum order qty",
                "is_storable": True,
                "list_price": 50.0,
                "route_ids": [(6, 0, [route_buy])],
                "seller_ids": [(0, 0, {"partner_id": vendor1.id, "price": 10.0})],
            }
        )
        cls.product_mrp_area_obj.create(
            {
                "product_id": cls.prod_max.id,
                "mrp_area_id": cls.mrp_area.id,
                "mrp_minimum_order_qty": 50.0,
                "mrp_maximum_order_qty": 100.0,
                "mrp_qty_multiple": 1.0,
            }
        )
        cls.prod_multiple = cls.product_obj.create(
            {
                "name": "Product with qty multiple",
                "is_storable": True,
                "list_price": 50.0,
                "route_ids": [(6, 0, [route_buy])],
                "seller_ids": [(0, 0, {"partner_id": vendor1.id, "price": 10.0})],
            }
        )
        cls.product_mrp_area_obj.create(
            {
                "product_id": cls.prod_multiple.id,
                "mrp_area_id": cls.mrp_area.id,
                "mrp_minimum_order_qty": 50.0,
                "mrp_maximum_order_qty": 500.0,
                "mrp_qty_multiple": 25.0,
            }
        )
        # Create more products to test special corner case scenarios:
        cls.product_scenario_1 = cls.product_obj.create(
            {
                "name": "Product Special Scenario 1",
                "is_storable": True,
                "list_price": 100.0,
                "route_ids": [(6, 0, [route_buy])],
                "seller_ids": [(0, 0, {"partner_id": vendor1.id, "price": 20.0})],
            }
        )
        cls.product_mrp_area_obj.create(
            {
                "product_id": cls.product_scenario_1.id,
                "mrp_area_id": cls.cases_area.id,
                "mrp_nbr_days": 7,
                "mrp_qty_multiple": 5.0,
            }
        )
        # Another product:
        cls.product_tz = cls.product_obj.create(
            {
                "name": "Product Timezone",
                "is_storable": True,
                "list_price": 100.0,
                "route_ids": [(6, 0, [route_buy])],
                "seller_ids": [(0, 0, {"partner_id": vendor1.id, "price": 20.0})],
            }
        )
        cls.product_mrp_area_obj.create(
            {"product_id": cls.product_tz.id, "mrp_area_id": cls.cases_area.id}
        )
        # Product to test special case with Purchase Uom:
        cls.prod_uom_test = cls.product_obj.create(
            {
                "name": "Product Uom Test",
                "is_storable": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "list_price": 150.0,
                "route_ids": [(6, 0, [route_buy])],
                "seller_ids": [(0, 0, {"partner_id": vendor1.id, "price": 20.0})],
            }
        )
        cls.product_mrp_area_obj.create(
            {"product_id": cls.prod_uom_test.id, "mrp_area_id": cls.mrp_area.id}
        )
        # Product to test lots
        cls.product_lots = cls.product_obj.create(
            {
                "name": "Product Tracked by Lots",
                "is_storable": True,
                "tracking": "lot",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "list_price": 100.0,
                "route_ids": [(6, 0, [route_buy])],
                "seller_ids": [(0, 0, {"partner_id": vendor1.id, "price": 25.0})],
            }
        )
        cls.product_mrp_area_obj.create(
            {"product_id": cls.product_lots.id, "mrp_area_id": cls.mrp_area.id}
        )
        cls.lot_1 = cls.lot_obj.create(
            {
                "product_id": cls.product_lots.id,
                "name": "Lot 1",
                "company_id": cls.company.id,
            }
        )
        cls.lot_2 = cls.lot_obj.create(
            {
                "product_id": cls.product_lots.id,
                "name": "Lot 2",
                "company_id": cls.company.id,
            }
        )
        cls.quant_obj.sudo().create(
            {
                "product_id": cls.product_lots.id,
                "lot_id": cls.lot_1.id,
                "quantity": 100.0,
                "location_id": cls.stock_location.id,
            }
        )
        cls.quant_obj.sudo().create(
            {
                "product_id": cls.product_lots.id,
                "lot_id": cls.lot_2.id,
                "quantity": 110.0,
                "location_id": cls.stock_location.id,
            }
        )
        # Product to test multi-step routes
        cls.product_routes = cls.product_obj.create(
            {
                "name": "Product Multi-step Routes",
                "is_storable": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "list_price": 100.0,
                "route_ids": [(6, 0, [route_buy])],
                "seller_ids": [(0, 0, {"partner_id": vendor1.id, "price": 35.0})],
            }
        )
        cls.product_mrp_area_obj.create(
            {"product_id": cls.product_routes.id, "mrp_area_id": cls.mrp_area.id}
        )

        # Product MRP Parameter to test supply method computation
        cls.env.ref("stock.route_warehouse0_mto").active = True
        cls.env["stock.rule"].create(
            {
                "name": "WH2: Main Area → Secondary Area (MTO)",
                "action": "pull",
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_src_id": cls.env.ref("stock.stock_location_stock").id,
                "location_dest_id": cls.sec_loc.id,
                "route_id": cls.env.ref("stock.route_warehouse0_mto").id,
                "procure_method": "mts_else_mto",
            }
        )
        cls.product_mrp_area_obj.create(
            {"product_id": cls.fp_4.id, "mrp_area_id": cls.secondary_area.id}
        )

        # Create pickings for Scenario 1:
        dt_base = cls.calendar.plan_days(3 + 1, datetime.today())
        cls._create_picking_in(
            cls.product_scenario_1, 87, dt_base, location=cls.cases_loc
        )
        dt_bit_later = dt_base + timedelta(hours=1)
        cls._create_picking_out(
            cls.product_scenario_1, 124, dt_bit_later, location=cls.cases_loc
        )
        dt_base_2 = cls.calendar.plan_days(3 + 1, datetime.today())
        cls._create_picking_out(
            cls.product_scenario_1, 90, dt_base_2, location=cls.cases_loc
        )

        dt_next_group = cls.calendar.plan_days(10 + 1, datetime.today())
        cls._create_picking_out(
            cls.product_scenario_1, 18, dt_next_group, location=cls.cases_loc
        )

        # product_4b will use the template bom (sequence 5)
        # (11, 22) = ("steel", "black")
        # create variant bom for product_4c (sequence 1)
        # (12, 21) = ("aluminum", "white")
        cls.mrp_bom_obj.create(
            {
                "product_tmpl_id": cls.product_4c.product_tmpl_id.id,
                "product_id": cls.product_4c.id,
                "type": "normal",
                "sequence": 1,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.av_12.id,
                            "product_qty": 1.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.av_21.id,
                            "product_qty": 1.0,
                        },
                    ),
                ],
            }
        )

        # Create test picking for FP-1, FP-2, Desk(steel, black),  Desk(aluminum, white)
        res = cls.calendar.plan_days(7 + 1, datetime.today().replace(hour=0))
        date_move = res.date()
        cls.picking_1 = cls.stock_picking_obj.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "scheduled_date": date_move,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.fp_1.id,
                            "date": date_move,
                            "product_uom": cls.fp_1.uom_id.id,
                            "product_uom_qty": 100,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.fp_2.id,
                            "date": date_move,
                            "product_uom": cls.fp_2.uom_id.id,
                            "product_uom_qty": 15,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.fp_3.id,
                            "date": date_move,
                            "product_uom": cls.fp_3.uom_id.id,
                            "product_uom_qty": 5,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_4b.id,
                            "date": date_move,
                            "product_uom": cls.product_4b.uom_id.id,
                            "product_uom_qty": 150,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_4c.id,
                            "date": date_move,
                            "product_uom": cls.product_4c.uom_id.id,
                            "product_uom_qty": 56,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    ),
                ],
            }
        )
        cls.picking_1.action_confirm()

        # Create test picking for procure qty adjustment tests:
        cls.picking_2 = cls.stock_picking_obj.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "scheduled_date": date_move,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.prod_min.id,
                            "date": date_move,
                            "product_uom": cls.prod_min.uom_id.id,
                            "product_uom_qty": 16,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.prod_max.id,
                            "date": date_move,
                            "product_uom": cls.prod_max.uom_id.id,
                            "product_uom_qty": 140,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.prod_multiple.id,
                            "date": date_move,
                            "product_uom": cls.prod_multiple.uom_id.id,
                            "product_uom_qty": 112,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    ),
                ],
            }
        )
        cls.picking_2.action_confirm()

        # Create Test PO:
        date_po = cls.calendar.plan_days(1 + 1, datetime.today().replace(hour=0)).date()
        cls.po = cls.po_obj.create(
            {
                "name": "Test PO-001",
                "partner_id": cls.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Test PP-2 line",
                            "product_id": cls.pp_2.id,
                            "date_planned": date_po,
                            "product_qty": 5.0,
                            "product_uom_id": cls.pp_2.uom_id.id,
                            "price_unit": 25.0,
                        },
                    )
                ],
            }
        )
        # Create Test PO for special case Puchase uom:
        # Remember that prod_uom_test had a UoM of units but it is purchased in dozens.
        # For this reason buying 1 quantity of it, means to have 12 units in stock.
        date_po = cls.calendar.plan_days(1 + 1, datetime.today().replace(hour=0)).date()
        cls.po_uom = cls.po_obj.create(
            {
                "name": "Test PO-002",
                "partner_id": cls.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Product Uom Test line",
                            "product_id": cls.prod_uom_test.id,
                            "date_planned": date_po,
                            "product_qty": 1.0,
                            "product_uom_id": cls.env.ref("uom.product_uom_dozen").id,
                            "price_unit": 25.0,
                        },
                    )
                ],
            }
        )

        # Create test MO:
        date_mo = cls.calendar.plan_days(9 + 1, datetime.today().replace(hour=0)).date()
        bom_fp_2 = cls.env["mrp.bom"].search(
            [("product_tmpl_id", "=", cls.fp_2.product_tmpl_id.id)], limit=1
        )
        cls.mo = cls._create_mo(cls.fp_2, bom_fp_2, date_mo, qty=12.0)

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

        # Create pickings:
        cls._create_picking_out(cls.product_lots, 25, today)

        cls.mrp_multi_level_wiz.create({}).run_mrp_multi_level()

    @classmethod
    def create_demand_sec_loc(cls, date_move, qty):
        return cls.stock_picking_obj.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.sec_loc.id,
                "location_dest_id": cls.customer_location.id,
                "scheduled_date": date_move,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.prod_test.id,
                            "date": date_move,
                            "product_uom": cls.prod_test.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": cls.sec_loc.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    )
                ],
            }
        )

    @classmethod
    def _create_user(cls, login, groups, company):
        user = cls.res_users.create(
            {
                "name": login,
                "login": login,
                "password": "demo",
                "email": "example@yourcompany.com",
                "company_id": company.id,
                "group_ids": [(6, 0, [group.id for group in groups])],
            }
        )
        return user

    @classmethod
    def _create_picking_in(cls, product, qty, date_move, location=None):
        if not location:
            location = cls.stock_location
        picking = cls.stock_picking_obj.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": location.id,
                "scheduled_date": date_move,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "date": date_move,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": location.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    @classmethod
    def _create_picking_out(cls, product, qty, date_move, location=None):
        if not location:
            location = cls.stock_location
        picking = cls.stock_picking_obj.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": location.id,
                "location_dest_id": cls.customer_location.id,
                "scheduled_date": date_move,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "date": date_move,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    @classmethod
    def _create_mo(cls, product, bom, date, qty=10.0):
        mo_form = Form(cls.mo_obj)
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = qty
        mo_form.date_start = date
        mo = mo_form.save()
        # Confirm the MO to generate stock moves:
        mo.action_confirm()
        return mo

    @classmethod
    def _run_procurement(
        cls, product, location=None, product_qty=10.0, extra_values=None
    ):
        if not location:
            location = cls.customer_location
        values = {"warehouse_id": cls.wh}
        if extra_values and isinstance(extra_values, dict):
            values.update(extra_values)
        return cls.env["stock.rule"].run(
            [
                cls.env["stock.rule"].Procurement(
                    product,
                    product_qty,
                    product.uom_id,
                    location,
                    product.name,
                    "/",
                    cls.env.company,
                    values,
                )
            ]
        )

    @classmethod
    def _create_demo_data(cls):
        # Create Partner
        cls.env["res.partner"].create({"name": "Lazer Tech", "is_company": True})

        # Create MRP Area
        cls.env["mrp.area"].create(
            {
                "name": "Test Area",
                "warehouse_id": cls.env.ref("stock.warehouse0").id,
                "location_id": cls.env.ref("stock.warehouse0").lot_stock_id.id,
            }
        )

        # Create Category
        categ_mrp = cls.env["product.category"].create({"name": "MRP"})

        # Create Products
        route_manufacture = cls.env.ref("mrp.route_warehouse0_manufacture")
        route_buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        uom_unit = cls.env.ref("uom.product_uom_unit")
        products_data = [
            ("FP-1", route_manufacture),
            ("FP-2", route_manufacture),
            ("FP-3", route_manufacture),
            ("FP-4", route_manufacture),
            ("SF-1", route_manufacture),
            ("SF-2", route_manufacture),
            ("SF-3", route_manufacture),
            ("PP-1", route_buy),
            ("PP-2", route_buy),
            ("PP-3", route_buy),
            ("PP-4", route_buy),
            ("AV-11 steel", route_buy),
            ("AV-12 aluminium", route_buy),
            ("AV-21 white", route_buy),
            ("AV-22 black", route_buy),
        ]
        for name, route in products_data:
            cls.env["product.product"].create(
                {
                    "name": name,
                    "categ_id": categ_mrp.id,
                    "is_storable": True,
                    "uom_id": uom_unit.id,
                    "route_ids": [(6, 0, [route.id])],
                }
            )

        # Create Product with variants
        attr1 = cls.env["product.attribute"].create({"name": "Material"})
        attr2 = cls.env["product.attribute"].create({"name": "Color"})
        attr1_v1 = cls.env["product.attribute.value"].create(
            [
                {
                    "name": "Steel",
                    "attribute_id": attr1.id,
                }
            ]
        )
        attr1_v2 = cls.env["product.attribute.value"].create(
            [
                {
                    "name": "Aluminium",
                    "attribute_id": attr1.id,
                }
            ]
        )
        attr2_v1 = cls.env["product.attribute.value"].create(
            [
                {
                    "name": "White",
                    "attribute_id": attr2.id,
                }
            ]
        )
        attr2_v2 = cls.env["product.attribute.value"].create(
            [
                {
                    "name": "Black",
                    "attribute_id": attr2.id,
                }
            ]
        )
        product_4 = cls.env["product.template"].create(
            {
                "name": "product.product_product_4",
                "categ_id": categ_mrp.id,
                "is_storable": True,
                "uom_id": uom_unit.id,
                "route_ids": [(6, 0, [route_manufacture.id])],
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attr1.id,
                            "value_ids": [(6, 0, [attr1_v1.id, attr1_v2.id])],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": attr2.id,
                            "value_ids": [(6, 0, [attr2_v1.id, attr2_v2.id])],
                        },
                    ),
                ],
            }
        )
        product_4b = product_4.product_variant_ids.filtered(
            lambda p: p.product_template_variant_value_ids.mapped("name")
            == ["Steel", "Black"]
        )
        product_4c = product_4.product_variant_ids.filtered(
            lambda p: p.product_template_variant_value_ids.mapped("name")
            == ["Aluminium", "White"]
        )
        product_4b.default_code = "product.product_product_4b"
        product_4c.default_code = "product.product_product_4c"

        # Create MRP Areas for products
        products_to_area = [
            "FP-1",
            "FP-2",
            "FP-3",
            "SF-1",
            "SF-2",
            "SF-3",
            "PP-1",
            "PP-2",
            "PP-3",
            "PP-4",
            "AV-11 steel",
            "AV-12 aluminium",
            "AV-21 white",
            "AV-22 black",
            "product.product_product_4",
        ]
        mrp_area = cls.env["mrp.area"].search([("name", "=", "Test Area")], limit=1)
        for name in products_to_area:
            product = cls.env["product.template"].search([("name", "=", name)], limit=1)
            for variant in product.product_variant_ids:
                cls.env["product.mrp.area"].create(
                    {"product_id": variant.id, "mrp_area_id": mrp_area.id}
                )

        # Create Supplier Info
        partner = cls.env["res.partner"].search([("name", "=", "Lazer Tech")], limit=1)
        supplier_info_data = [
            ("AV-11 steel", 4, 100),
            ("AV-12 aluminium", 4, 100),
            ("AV-21 white", 4, 100),
            ("AV-22 black", 4, 100),
            ("PP-1", 4, 100),
            ("PP-2", 2, 100),
            ("PP-3", 2, 10),
            ("PP-4", 3, 80),
        ]
        for name, delay, price in supplier_info_data:
            product = cls.env["product.product"].search([("name", "=", name)], limit=1)
            cls.env["product.supplierinfo"].create(
                {
                    "product_tmpl_id": product.product_tmpl_id.id,
                    "partner_id": partner.id,
                    "delay": delay,
                    "min_qty": 0,
                    "price": price,
                }
            )

        # Create BOMs
        # FP-1
        fp1 = cls.env["product.product"].search([("name", "=", "FP-1")], limit=1)
        pp1 = cls.env["product.product"].search([("name", "=", "PP-1")], limit=1)
        pp2 = cls.env["product.product"].search([("name", "=", "PP-2")], limit=1)
        bom_fp1 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": fp1.product_tmpl_id.id,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "produce_delay": 2,
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": pp1.id,
                "product_qty": 2,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "bom_id": bom_fp1.id,
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": pp2.id,
                "product_qty": 3,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "bom_id": bom_fp1.id,
            }
        )

        # FP-2
        fp2 = cls.env["product.product"].search([("name", "=", "FP-2")], limit=1)
        sf1 = cls.env["product.product"].search([("name", "=", "SF-1")], limit=1)
        sf2 = cls.env["product.product"].search([("name", "=", "SF-2")], limit=1)
        bom_fp2 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": fp2.product_tmpl_id.id,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "produce_delay": 1,
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": sf1.id,
                "product_qty": 2,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "bom_id": bom_fp2.id,
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": sf2.id,
                "product_qty": 3,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "bom_id": bom_fp2.id,
            }
        )

        # FP-3
        fp3 = cls.env["product.product"].search([("name", "=", "FP-3")], limit=1)
        sf3 = cls.env["product.product"].search([("name", "=", "SF-3")], limit=1)
        pp3 = cls.env["product.product"].search([("name", "=", "PP-3")], limit=1)
        bom_fp3 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": fp3.product_tmpl_id.id,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "produce_delay": 3,
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": sf3.id,
                "product_qty": 2,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "bom_id": bom_fp3.id,
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": pp3.id,
                "product_qty": 2,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "bom_id": bom_fp3.id,
            }
        )

        # SF-1
        bom_sf1 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": sf1.product_tmpl_id.id,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "produce_delay": 1,
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": pp1.id,
                "product_qty": 3,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "bom_id": bom_sf1.id,
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": pp2.id,
                "product_qty": 2,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "bom_id": bom_sf1.id,
            }
        )

        # SF-2
        bom_sf2 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": sf2.product_tmpl_id.id,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "produce_delay": 3,
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": pp2.id,
                "product_qty": 3,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "bom_id": bom_sf2.id,
            }
        )

        # SF-3
        pp4 = cls.env["product.product"].search([("name", "=", "PP-4")], limit=1)
        bom_sf3 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": sf3.product_tmpl_id.id,
                "product_uom_id": uom_unit.id,
                "type": "phantom",
                "sequence": 5,
                "produce_delay": 3,
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": pp3.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "bom_id": bom_sf3.id,
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": pp4.id,
                "product_qty": 3,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
                "bom_id": bom_sf3.id,
            }
        )

        # Customizable Desk (Product 4)
        av11 = cls.env["product.product"].search(
            [("name", "=", "AV-11 steel")], limit=1
        )
        av12 = cls.env["product.product"].search(
            [("name", "=", "AV-12 aluminium")], limit=1
        )
        av21 = cls.env["product.product"].search(
            [("name", "=", "AV-21 white")], limit=1
        )
        av22 = cls.env["product.product"].search(
            [("name", "=", "AV-22 black")], limit=1
        )

        bom_p4 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": product_4.id,
                "product_uom_id": uom_unit.id,
                "sequence": 5,
            }
        )

        cls.env["mrp.bom.line"].create(
            {
                "product_id": av11.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 1,
                "bom_id": bom_p4.id,
                "bom_product_template_attribute_value_ids": [(6, 0, [attr1_v1.id])],
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": av12.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 2,
                "bom_id": bom_p4.id,
                "bom_product_template_attribute_value_ids": [(6, 0, [attr1_v2.id])],
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": av21.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 3,
                "bom_id": bom_p4.id,
                "bom_product_template_attribute_value_ids": [(6, 0, [attr2_v1.id])],
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "product_id": av22.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 4,
                "bom_id": bom_p4.id,
                "bom_product_template_attribute_value_ids": [(6, 0, [attr2_v2.id])],
            }
        )

        # Initial Inventory
        location_stock = cls.env.ref("stock.warehouse0").lot_stock_id
        cls.env["stock.quant"].create(
            {
                "product_id": pp1.id,
                "product_uom_id": uom_unit.id,
                "inventory_quantity": 10,
                "location_id": location_stock.id,
            }
        ).action_apply_inventory()
        cls.env["stock.quant"].create(
            {
                "product_id": pp2.id,
                "product_uom_id": uom_unit.id,
                "inventory_quantity": 20,
                "location_id": location_stock.id,
            }
        ).action_apply_inventory()
        cls.env["stock.quant"].create(
            {
                "product_id": sf2.id,
                "product_uom_id": uom_unit.id,
                "inventory_quantity": 15,
                "location_id": location_stock.id,
            }
        ).action_apply_inventory()
        cls.env["stock.quant"].create(
            {
                "product_id": product_4b.id,
                "product_uom_id": uom_unit.id,
                "inventory_quantity": 50,
                "location_id": location_stock.id,
            }
        ).action_apply_inventory()
        cls.env["stock.quant"].create(
            {
                "product_id": product_4c.id,
                "product_uom_id": uom_unit.id,
                "inventory_quantity": 55,
                "location_id": location_stock.id,
            }
        ).action_apply_inventory()
