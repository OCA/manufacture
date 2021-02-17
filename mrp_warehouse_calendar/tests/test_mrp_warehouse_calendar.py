# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestMrpWarehouseCalendar(TransactionCase):
    def setUp(self):
        super(TestMrpWarehouseCalendar, self).setUp()
        self.move_obj = self.env["stock.move"]
        self.pg_obj = self.env["procurement.group"]

        self.company = self.env.ref("base.main_company")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.customer_loc = self.env.ref("stock.stock_location_customers")
        self.company_partner = self.env.ref("base.main_partner")
        self.calendar = self.env.ref("resource.resource_calendar_std")
        self.manufacture_route = self.env.ref("mrp.route_warehouse0_manufacture")

        self.warehouse.calendar_id = self.calendar.id
        self.warehouse_2 = self.env["stock.warehouse"].create(
            {"code": "WH-T", "name": "Warehouse Test", "calendar_id": self.calendar.id}
        )

        self.product = self.env["product.product"].create(
            {
                "name": "test product",
                "default_code": "PRD",
                "type": "product",
                "produce_delay": 1,
            }
        )
        self.product_2 = self.env["product.product"].create(
            {"name": "test product 2", "default_code": "PRD 2", "type": "product"}
        )
        self.bom = self.env["mrp.bom"].create(
            {
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_uom_id": self.product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        self.env["mrp.bom.line"].create(
            {"bom_id": self.bom.id, "product_id": self.product_2.id, "product_qty": 2}
        )

        self.product.route_ids = [(6, 0, self.manufacture_route.ids)]

    def test_procurement_with_calendar(self):
        values = {
            "date_planned": "2097-01-07 09:00:00",  # Monday
            "warehouse_id": self.warehouse,
            "company_id": self.company,
            "rule_id": self.manufacture_route,
        }
        self.pg_obj.run(
            [
                self.pg_obj.Procurement(
                    self.product,
                    100,
                    self.product.uom_id,
                    self.warehouse.lot_stock_id,
                    "Test",
                    "Test",
                    self.warehouse.company_id,
                    values,
                )
            ]
        )
        mo = self.env["mrp.production"].search(
            [("product_id", "=", self.product.id)], limit=1
        )
        date_plan_start = fields.Date.to_date(mo.date_planned_start)
        # Friday 4th Jan 2097
        friday = fields.Date.to_date("2097-01-04 09:00:00")

        self.assertEqual(date_plan_start, friday)

    def test_procurement_with_calendar_02(self):
        """Test procuring at the beginning of the day, with no work intervals
        before."""
        values = {
            "date_planned": "2097-01-07 01:00:00",  # Monday
            "warehouse_id": self.warehouse,
            "company_id": self.company,
            "rule_id": self.manufacture_route,
        }
        self.pg_obj.run(
            [
                self.pg_obj.Procurement(
                    self.product,
                    100,
                    self.product.uom_id,
                    self.warehouse.lot_stock_id,
                    "Test 2",
                    "Test 2",
                    self.warehouse.company_id,
                    values,
                )
            ]
        )
        mo = self.env["mrp.production"].search(
            [("product_id", "=", self.product.id)], limit=1
        )
        date_plan_start = fields.Date.to_date(mo.date_planned_start)
        # Friday 4th Jan 2097
        friday = fields.Date.to_date("2097-01-04 09:00:00")

        self.assertEqual(date_plan_start, friday)

    def test_onchange_date_planned(self):
        mo = self.env["mrp.production"].new(
            {
                "product_id": self.product.id,
                "bom_id": self.bom.id,
                "product_qty": 1,
                "picking_type_id": self.env[
                    "mrp.production"
                ]._get_default_picking_type(),
            }
        )
        mo.date_planned_start = "2097-01-04 09:00:00"
        mo.onchange_date_planned()
        date_plan_finished = fields.Date.to_date(mo.date_planned_finished)
        monday = fields.Date.to_date("2097-01-07 09:00:00")
        self.assertEqual(date_plan_finished, monday)
