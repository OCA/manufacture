# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class MrpProductionCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(MrpProductionCase, self).setUp(*args, **kwargs)

        self.obj_group = self.env["procurement.group"]
        self.obj_mo = self.env["mrp.production"]

        self.warehouse1 = self.env.ref("stock.warehouse0")
        self.warehouse2 = self.env["stock.warehouse"].create({
            "name": "X Warehouse",
            "code": "X WH",
            "reception_steps": "one_step",
            "delivery_steps": "ship_only",
            "resupply_from_wh": False,
            "default_resupply_wh_id": False,
        })
        self.loc_stock_2 = self.warehouse2.lot_stock_id
        self.loc_production = self.env.ref(
            "stock.location_production")
        self.route = self.env["stock.location.route"].create({
            "name": "X Route",
            "sequence": 1,
            "product_selectable": True,
        })
        self.rule = self.env["procurement.rule"].create({
            "name": "X Production",
            "location_id": self.loc_production.id,
            "location_src_id": self.loc_stock_2.id,
            "procure_method": "make_to_order",
            "picking_type_id": self.warehouse2.int_type_id.id,
            "action": "move",
            "sequence": 1,
            "route_id": self.route.id,
        })
        self.product1 = self.env.ref("product.product_product_18")
        self.product_raw1 = self.env.ref("product.product_product_17")
        self.product_raw1.write({
            "route_ids": [(4, self.route.id)],
        })
        self.bom1 = self.env.ref("mrp.mrp_bom_3")
        self.bom1.write({
            "routing_id": False})

    def _create_procurement_group(
            self, name):
        res = {
            "name": name,
            "move_type": "direct"
        }
        return self.obj_group.create(res)

    def _create_mo(
            self,
            product=False,
            bom=False,
            src_loc=False,
            dest_loc=False,
            group=False,
            qty=10.0):
        if not product:
            product = self.product1
            uom = product.uom_id
        if not bom:
            bom = self.bom1
        if not src_loc:
            src_loc = self.loc_stock_2
        if not dest_loc:
            dest_loc = self.loc_stock_2
        res = {
            "product_id": product.id,
            "bom_id": bom.id,
            "location_src_id": src_loc.id,
            "location_dest_id": dest_loc.id,
            "raw_material_procurement_group_id": group,
            "product_qty": qty,
            "product_uom": uom.id,
        }
        return self.obj_mo.create(res)

    def test_1(self):
        # Create MO
        mo = self._create_mo()
        # Click confirm button
        mo.signal_workflow("button_confirm")
        for raw in mo.move_lines:
            self.assertEqual(
                raw.location_id,
                self.loc_stock_2)
            self.assertEqual(
                raw.location_dest_id,
                self.loc_production)
            self.assertEqual(
                raw.procure_method,
                "make_to_order")
            self.assertEqual(
                len(raw.group_id),
                0)

    def test_2(self):
        group1 = self._create_procurement_group(
            "X 001")
        # Create MO
        mo = self._create_mo(
            group=group1.id)
        # Click confirm button
        mo.signal_workflow("button_confirm")
        for raw in mo.move_lines:
            self.assertEqual(
                raw.location_id,
                self.loc_stock_2)
            self.assertEqual(
                raw.location_dest_id,
                self.loc_production)
            self.assertEqual(
                raw.procure_method,
                "make_to_order")
            self.assertEqual(
                raw.group_id,
                group1)
