# -*- coding: utf-8 -*-
# © 2015 Daniel Campos
# © 2015 Pedro M. Baeza
# © 2015 Ana Juaristi
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime
from openerp import exceptions


class TestOperation(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestOperation, self).setUp(*args, **kwargs)

        self.obj_production = self.env["mrp.production"]

        self.location = self.env.ref("stock.stock_location_14")
        self.bom = self.env.ref("mrp.mrp_bom_11")
        self.routing = self.env.ref("mrp.mrp_routing_1")
        self.product = self.env.ref("product.product_product_4b")
        self.routing_wc = self.env.ref("mrp.mrp_routing_workcenter_4")
        # self.routning_wc.write({"init_without_material": True})

        self.prod_data = {
            "date_planned": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location_dest_id": self.location.id,
            "location_src_id": self.location.id,
            "product_id": self.product.id,
            "product_qty": 1.0,
            "product_uom": self.product.uom_id.id,
            "bom_id": self.bom.id,
            "routing_id": self.routing.id,
        }

        return result

    def test_1(self):
        production = self.obj_production.create(self.prod_data)
        production.signal_workflow("button_confirm")

        # MO should be in Confirm state
        self.assertEqual(
            production.state,
            "confirmed")

        # MO should have equal operation as routing workcenter
        self.assertEqual(
            len(production.workcenter_lines),
            len(self.routing.workcenter_lines))

        wo = production.workcenter_lines[0]

        # WO can not start without material
        with self.assertRaises(exceptions.Warning):
            wo.signal_workflow("button_start_working")

    def test_2(self):
        self.routing.workcenter_lines.write({
            "init_without_material": True})
        production = self.obj_production.create(self.prod_data)
        production.signal_workflow("button_confirm")
        # MO should be in Confirm state
        self.assertEqual(
            production.state,
            "confirmed")

        # MO should have equal operation as routing workcenter
        self.assertEqual(
            len(production.workcenter_lines),
            len(self.routing.workcenter_lines))

        wo = production.workcenter_lines[0]
        wo.signal_workflow("button_start_working")

        # WO should start
        self.assertEqual(
            wo.state,
            "startworking")
