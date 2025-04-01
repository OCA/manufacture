# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpProductionQuantManualAssign(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.quant_assign_wizard = cls.env["assign.manual.quants"]
        cls.parent_serial = cls.env["product.product"].create(
            {"name": "Parent - Serial", "type": "product", "tracking": "serial"}
        )
        cls.component_normal = cls.env["product.product"].create(
            {"name": "Component - Normal", "type": "product", "tracking": "none"}
        )
        cls.component_lot = cls.env["product.product"].create(
            {"name": "Component - Lot", "type": "product", "tracking": "lot"}
        )
        cls.component_serial = cls.env["product.product"].create(
            {"name": "Component - Serial", "type": "product", "tracking": "serial"}
        )
        cls.component_consumable = cls.env["product.product"].create(
            {"name": "Component - Consumable", "type": "consu"}
        )
        cls.location_src = cls.env.ref("stock.stock_location_stock")
        cls.location1 = cls._create_location(cls, "Location 1")
        cls.location2 = cls._create_location(cls, "Location 2")
        cls.location3 = cls._create_location(cls, "Location 3")

        cls.bom_serial = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.parent_serial.product_tmpl_id.id,
                "product_id": cls.parent_serial.id,
                "product_qty": 1,
                "type": "normal",
                "product_uom_id": cls.parent_serial.uom_id.id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": c.id,
                            "product_qty": 1,
                            "product_uom_id": c.uom_id.id,
                        },
                    )
                    for c in [
                        cls.component_normal,
                        cls.component_lot,
                        cls.component_serial,
                        cls.component_consumable,
                    ]
                ],
            }
        )

        cls.quant_component_normal_1 = cls._create_quant(
            cls, cls.component_normal, 100.0, cls.location1
        )
        cls.quant_component_normal_2 = cls._create_quant(
            cls, cls.component_normal, 100.0, cls.location2
        )
        cls.quant_component_normal_3 = cls._create_quant(
            cls, cls.component_normal, 100.0, cls.location3
        )

        cls.quant_component_lot_1 = cls._create_quant(
            cls, cls.component_lot, 100.0, cls.location1, offset=0
        )
        cls.quant_component_lot_2 = cls._create_quant(
            cls, cls.component_lot, 100.0, cls.location2, offset=200
        )
        cls.quant_component_lot_3 = cls._create_quant(
            cls, cls.component_lot, 100.0, cls.location3, offset=400
        )

        cls.quant_component_serial_1 = cls._create_quant(
            cls, cls.component_serial, 100.0, cls.location1, offset=0
        )
        cls.quant_component_serial_2 = cls._create_quant(
            cls, cls.component_serial, 100.0, cls.location2, offset=200
        )
        cls.quant_component_serial_3 = cls._create_quant(
            cls, cls.component_serial, 100.0, cls.location3, offset=400
        )

        cls.mo_1 = cls.env["mrp.production"].create(
            {
                "name": "MO 1",
                "product_id": cls.parent_serial.id,
                "product_uom_id": cls.parent_serial.uom_id.id,
                "product_qty": 2,
                "bom_id": cls.bom_serial.id,
                "location_src_id": cls.location_src.id,
            }
        )
        cls.mo_1.action_confirm()

        cls.move_normal = cls.mo_1.move_raw_ids.filtered(
            lambda m: m.product_id == cls.component_normal
        )
        cls.move_lot = cls.mo_1.move_raw_ids.filtered(
            lambda m: m.product_id == cls.component_lot
        )
        cls.move_serial = cls.mo_1.move_raw_ids.filtered(
            lambda m: m.product_id == cls.component_serial
        )
        cls.move_consumable = cls.mo_1.move_raw_ids.filtered(
            lambda m: m.product_id == cls.component_consumable
        )

    def _create_location(self, name):
        return self.env["stock.location"].create(
            {"name": name, "usage": "internal", "location_id": self.location_src.id}
        )

    def _create_quant(self, product, qty, location, offset=0):
        i = 1
        name = "L"
        if product.tracking == "serial":
            i, qty = int(qty), 1
            name = "S"

        vals = []
        for x in range(1, i + 1):
            qDict = {
                "location_id": location.id,
                "product_id": product.id,
                "quantity": qty,
            }

            if product.tracking != "none":
                qDict["lot_id"] = (
                    self.env["stock.lot"]
                    .create(
                        {
                            "name": name + str(offset + x),
                            "product_id": product.id,
                            "company_id": self.env.company.id,
                        }
                    )
                    .id
                )
            vals.append(qDict)

        return self.env["stock.quant"].create(vals)

    def _create_wizard(self, move, mo):
        return Form(
            self.env["assign.manual.quants"].with_context(
                active_id=move.id, active_mo_id=mo.id
            )
        ).save()

    def test_01_lines_created(self):
        # Test the numbers of quants_lines should be appearing:

        wizard = self._create_wizard(self.move_normal, self.mo_1)
        self.assertEqual(
            len(wizard.quants_lines.ids),
            3,
            "Three quants created, three quants got by default",
        )

        wizard = self._create_wizard(self.move_lot, self.mo_1)
        self.assertEqual(
            len(wizard.quants_lines.ids),
            3,
            "Three quants created, three quants got by default",
        )

        wizard = self._create_wizard(self.move_serial, self.mo_1)
        self.assertEqual(
            len(wizard.quants_lines.ids),
            300,
            "300 quants created, 300 quants got by default",
        )

        wizard = self._create_wizard(self.move_consumable, self.mo_1)
        self.assertEqual(
            len(wizard.quants_lines.ids),
            0,
            "No quants created, 0 quants got by default",
        )

    def test_02_select_normal_component(self):
        wizard = self._create_wizard(self.move_normal, self.mo_1)
        for ql in wizard.quants_lines:
            ql.selected = False
            ql.to_consume_now = False
            ql.qty = 0
        wizard.assign_quants()
        self.assertEqual(self.move_normal.quantity, 0)
        self.assertEqual(self.move_normal.picked, False)

        wizard = self._create_wizard(self.move_normal, self.mo_1)
        quant_line_2 = wizard.quants_lines.filtered(
            lambda ql: ql.location_id == self.location2
        )
        quant_line_2.selected = True
        quant_line_2.qty = 1
        quant_line_2.to_consume_now = False
        wizard.assign_quants()
        self.assertEqual(self.move_normal.quantity, 1)
        self.assertEqual(self.move_normal.picked, False)
        self.assertEqual(len(self.move_normal.move_line_ids), 1)
        self.assertEqual(self.move_normal.move_line_ids.location_id, self.location2)

        wizard = self._create_wizard(self.move_normal, self.mo_1)
        quant_line_2 = wizard.quants_lines.filtered(
            lambda ql: ql.location_id == self.location2
        )
        self.assertEqual(quant_line_2.selected, True)
        self.assertEqual(quant_line_2.qty, 1)
        self.assertEqual(quant_line_2.to_consume_now, False)
        quant_line_3 = wizard.quants_lines.filtered(
            lambda ql: ql.location_id == self.location3
        )
        quant_line_3.selected = True
        quant_line_3.qty = 1
        quant_line_3.to_consume_now = True
        wizard.assign_quants()
        self.assertEqual(self.move_normal.quantity, 2)
        self.assertEqual(self.move_normal.picked, True)
        self.assertEqual(len(self.move_normal.move_line_ids), 2)
        move_line_2 = self.move_normal.move_line_ids.filtered(
            lambda ml: ml.location_id == self.location2
        )
        move_line_3 = self.move_normal.move_line_ids.filtered(
            lambda ml: ml.location_id == self.location3
        )
        self.assertEqual(move_line_2.quantity, 1)
        self.assertEqual(move_line_2.picked, False)
        self.assertEqual(move_line_3.quantity, 1)
        self.assertEqual(move_line_3.picked, True)

        wizard = self._create_wizard(self.move_normal, self.mo_1)
        quant_line_2 = wizard.quants_lines.filtered(
            lambda ql: ql.location_id == self.location2
        )
        quant_line_3 = wizard.quants_lines.filtered(
            lambda ql: ql.location_id == self.location3
        )
        self.assertEqual(quant_line_2.selected, True)
        self.assertEqual(quant_line_2.qty, 1)
        self.assertEqual(quant_line_2.to_consume_now, False)
        self.assertEqual(quant_line_3.selected, True)
        self.assertEqual(quant_line_3.qty, 1)
        self.assertEqual(quant_line_3.to_consume_now, True)
        quant_line_3.selected = False
        quant_line_3.qty = 0
        quant_line_3.to_consume_now = False
        quant_line_2.selected = True
        quant_line_2.qty = 2
        quant_line_2.to_consume_now = True
        wizard.assign_quants()
        self.assertEqual(self.move_normal.quantity, 2)
        self.assertEqual(self.move_normal.picked, True)
        self.assertEqual(len(self.move_normal.move_line_ids), 1)
        move_line_2 = self.move_normal.move_line_ids.filtered(
            lambda ml: ml.location_id == self.location2
        )
        self.assertEqual(move_line_2.quantity, 2)
        self.assertEqual(move_line_2.picked, True)

        wizard = self._create_wizard(self.move_normal, self.mo_1)
        quant_line_2 = wizard.quants_lines.filtered(
            lambda ql: ql.location_id == self.location2
        )
        quant_line_3 = wizard.quants_lines.filtered(
            lambda ql: ql.location_id == self.location3
        )
        self.assertEqual(quant_line_2.selected, True)
        self.assertEqual(quant_line_2.qty, 2)
        self.assertEqual(quant_line_2.to_consume_now, True)
        self.assertEqual(quant_line_3.selected, False)
        self.assertEqual(quant_line_3.qty, 0)
        self.assertEqual(quant_line_3.to_consume_now, False)
        quant_line_2.selected = True
        quant_line_2.qty = 2
        quant_line_2.to_consume_now = False
        wizard.assign_quants()
        self.assertEqual(self.move_normal.quantity, 2)
        self.assertEqual(self.move_normal.picked, False)
        self.assertEqual(len(self.move_normal.move_line_ids), 1)
        move_line_2 = self.move_normal.move_line_ids.filtered(
            lambda ml: ml.location_id == self.location2
        )
        self.assertEqual(move_line_2.quantity, 2)
        self.assertEqual(move_line_2.picked, False)

    def test_03_select_normal_component(self):
        lot_l201 = self.env["stock.lot"].search(
            [("name", "=", "L201"), ("product_id", "=", self.component_lot.id)]
        )
        self.assertTrue(lot_l201)
        lot_l401 = self.env["stock.lot"].search(
            [("name", "=", "L401"), ("product_id", "=", self.component_lot.id)]
        )
        self.assertTrue(lot_l401)
        wizard = self._create_wizard(self.move_lot, self.mo_1)
        for ql in wizard.quants_lines:
            ql.selected = False
            ql.to_consume_now = False
            ql.qty = 0
        wizard.assign_quants()
        self.assertEqual(self.move_lot.quantity, 0)
        self.assertEqual(self.move_lot.picked, False)

        wizard = self._create_wizard(self.move_lot, self.mo_1)
        quant_line_l201 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_l201)
        quant_line_l201.selected = True
        quant_line_l201.qty = 1
        quant_line_l201.to_consume_now = False
        wizard.assign_quants()
        self.assertEqual(self.move_lot.quantity, 1)
        self.assertEqual(self.move_lot.picked, False)
        self.assertEqual(len(self.move_lot.move_line_ids), 1)
        self.assertEqual(self.move_lot.move_line_ids.lot_id, lot_l201)

        wizard = self._create_wizard(self.move_lot, self.mo_1)
        quant_line_l201 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_l201)
        self.assertEqual(quant_line_l201.selected, True)
        self.assertEqual(quant_line_l201.qty, 1)
        self.assertEqual(quant_line_l201.to_consume_now, False)
        quant_line_3 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_l401)
        quant_line_3.selected = True
        quant_line_3.qty = 1
        quant_line_3.to_consume_now = True
        wizard.assign_quants()
        self.assertEqual(self.move_lot.quantity, 2)
        self.assertEqual(self.move_lot.picked, True)
        self.assertEqual(len(self.move_lot.move_line_ids), 2)
        move_line_l201 = self.move_lot.move_line_ids.filtered(
            lambda ml: ml.lot_id == lot_l201
        )
        move_line_3 = self.move_lot.move_line_ids.filtered(
            lambda ml: ml.lot_id == lot_l401
        )
        self.assertEqual(move_line_l201.quantity, 1)
        self.assertEqual(move_line_l201.picked, False)
        self.assertEqual(move_line_3.quantity, 1)
        self.assertEqual(move_line_3.picked, True)

        wizard = self._create_wizard(self.move_lot, self.mo_1)
        quant_line_l201 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_l201)
        quant_line_3 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_l401)
        self.assertEqual(quant_line_l201.selected, True)
        self.assertEqual(quant_line_l201.qty, 1)
        self.assertEqual(quant_line_l201.to_consume_now, False)
        self.assertEqual(quant_line_3.selected, True)
        self.assertEqual(quant_line_3.qty, 1)
        self.assertEqual(quant_line_3.to_consume_now, True)
        quant_line_3.selected = False
        quant_line_3.qty = 0
        quant_line_3.to_consume_now = False
        quant_line_l201.selected = True
        quant_line_l201.qty = 2
        quant_line_l201.to_consume_now = True
        wizard.assign_quants()
        self.assertEqual(self.move_lot.quantity, 2)
        self.assertEqual(self.move_lot.picked, True)
        self.assertEqual(len(self.move_lot.move_line_ids), 1)
        move_line_l201 = self.move_lot.move_line_ids.filtered(
            lambda ml: ml.lot_id == lot_l201
        )
        self.assertEqual(move_line_l201.quantity, 2)
        self.assertEqual(move_line_l201.picked, True)

        wizard = self._create_wizard(self.move_lot, self.mo_1)
        quant_line_l201 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_l201)
        quant_line_3 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_l401)
        self.assertEqual(quant_line_l201.selected, True)
        self.assertEqual(quant_line_l201.qty, 2)
        self.assertEqual(quant_line_l201.to_consume_now, True)
        self.assertEqual(quant_line_3.selected, False)
        self.assertEqual(quant_line_3.qty, 0)
        self.assertEqual(quant_line_3.to_consume_now, False)
        quant_line_l201.selected = True
        quant_line_l201.qty = 2
        quant_line_l201.to_consume_now = False
        wizard.assign_quants()
        self.assertEqual(self.move_lot.quantity, 2)
        self.assertEqual(self.move_lot.picked, False)
        self.assertEqual(len(self.move_lot.move_line_ids), 1)
        move_line_l201 = self.move_lot.move_line_ids.filtered(
            lambda ml: ml.lot_id == lot_l201
        )
        self.assertEqual(move_line_l201.quantity, 2)
        self.assertEqual(move_line_l201.picked, False)

    def test_04_select_normal_component(self):
        lot_s484 = self.env["stock.lot"].search(
            [("name", "=", "S484"), ("product_id", "=", self.component_serial.id)]
        )
        self.assertTrue(lot_s484)
        lot_s252 = self.env["stock.lot"].search(
            [("name", "=", "S252"), ("product_id", "=", self.component_serial.id)]
        )
        self.assertTrue(lot_s252)
        wizard = self._create_wizard(self.move_serial, self.mo_1)
        for ql in wizard.quants_lines:
            ql.selected = False
            ql.to_consume_now = False
            ql.qty = 0
        wizard.assign_quants()
        self.assertEqual(self.move_serial.quantity, 0)
        self.assertEqual(self.move_serial.picked, False)

        wizard = self._create_wizard(self.move_serial, self.mo_1)
        quant_line_s484 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_s484)
        quant_line_s484.selected = True
        quant_line_s484.qty = 1
        quant_line_s484.to_consume_now = False
        wizard.assign_quants()
        self.assertEqual(self.move_serial.quantity, 1)
        self.assertEqual(self.move_serial.picked, False)
        self.assertEqual(len(self.move_serial.move_line_ids), 1)
        self.assertEqual(self.move_serial.move_line_ids.lot_id, lot_s484)

        wizard = self._create_wizard(self.move_serial, self.mo_1)
        quant_line_s484 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_s484)
        self.assertEqual(quant_line_s484.selected, True)
        self.assertEqual(quant_line_s484.qty, 1)
        self.assertEqual(quant_line_s484.to_consume_now, False)
        quant_line_s252 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_s252)
        quant_line_s252.selected = True
        quant_line_s252.qty = 1
        quant_line_s252.to_consume_now = True
        wizard.assign_quants()
        self.assertEqual(self.move_serial.quantity, 2)
        self.assertEqual(self.move_serial.picked, True)
        self.assertEqual(len(self.move_serial.move_line_ids), 2)
        move_line_s484 = self.move_serial.move_line_ids.filtered(
            lambda ml: ml.lot_id == lot_s484
        )
        move_line_s252 = self.move_serial.move_line_ids.filtered(
            lambda ml: ml.lot_id == lot_s252
        )
        self.assertEqual(move_line_s484.quantity, 1)
        self.assertEqual(move_line_s484.picked, False)
        self.assertEqual(move_line_s252.quantity, 1)
        self.assertEqual(move_line_s252.picked, True)

        wizard = self._create_wizard(self.move_serial, self.mo_1)
        quant_line_s484 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_s484)
        quant_line_s252 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_s252)
        self.assertEqual(quant_line_s484.selected, True)
        self.assertEqual(quant_line_s484.qty, 1)
        self.assertEqual(quant_line_s484.to_consume_now, False)
        self.assertEqual(quant_line_s252.selected, True)
        self.assertEqual(quant_line_s252.qty, 1)
        self.assertEqual(quant_line_s252.to_consume_now, True)
        quant_line_s484.selected = True
        quant_line_s484.qty = 1
        quant_line_s484.to_consume_now = True
        wizard.assign_quants()
        self.assertEqual(self.move_serial.quantity, 2)
        self.assertEqual(self.move_serial.picked, True)
        self.assertEqual(len(self.move_serial.move_line_ids), 2)
        move_line_s484 = self.move_serial.move_line_ids.filtered(
            lambda ml: ml.lot_id == lot_s484
        )
        move_line_s252 = self.move_serial.move_line_ids.filtered(
            lambda ml: ml.lot_id == lot_s252
        )
        self.assertEqual(move_line_s484.quantity, 1)
        self.assertEqual(move_line_s484.picked, True)
        self.assertEqual(move_line_s252.quantity, 1)
        self.assertEqual(move_line_s252.picked, True)

        wizard = self._create_wizard(self.move_serial, self.mo_1)
        quant_line_s484 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_s484)
        quant_line_s252 = wizard.quants_lines.filtered(lambda ql: ql.lot_id == lot_s252)
        self.assertEqual(quant_line_s484.selected, True)
        self.assertEqual(quant_line_s484.qty, 1)
        self.assertEqual(quant_line_s484.to_consume_now, True)
        self.assertEqual(quant_line_s252.selected, True)
        self.assertEqual(quant_line_s252.qty, 1)
        self.assertEqual(quant_line_s252.to_consume_now, True)
        quant_line_s484.selected = True
        quant_line_s484.qty = 1
        quant_line_s484.to_consume_now = False
        quant_line_s252.selected = True
        quant_line_s252.qty = 1
        quant_line_s252.to_consume_now = False
        wizard.assign_quants()
        self.assertEqual(self.move_serial.quantity, 2)
        self.assertEqual(self.move_serial.picked, False)
        self.assertEqual(len(self.move_serial.move_line_ids), 2)
        move_line_s484 = self.move_serial.move_line_ids.filtered(
            lambda ml: ml.lot_id == lot_s484
        )
        move_line_s252 = self.move_serial.move_line_ids.filtered(
            lambda ml: ml.lot_id == lot_s252
        )
        self.assertEqual(move_line_s484.quantity, 1)
        self.assertEqual(move_line_s484.picked, False)
        self.assertEqual(move_line_s252.quantity, 1)
        self.assertEqual(move_line_s252.picked, False)
