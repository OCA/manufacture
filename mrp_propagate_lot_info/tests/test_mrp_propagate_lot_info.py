# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command
from odoo.tests import Form, common


class TestMrpPropagateLotInfo(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.lot_ref_field = cls.env["ir.model.fields"].search(
            [("model", "=", "stock.lot"), ("name", "=", "ref")], limit=1
        )
        cls.profile = cls.env["mrp.lot.info.propagation.profile"].create(
            {
                "name": "Lot reference",
                "propagate_lot_field_ids": [Command.set(cls.lot_ref_field.ids)],
            }
        )
        cls.category = cls.env["product.category"].create(
            {
                "name": "Lot propagation category",
                "mrp_propagate_lot_profile_id": cls.profile.id,
            }
        )
        cls.finished_product = cls.env.ref("mrp.product_product_computer_desk")
        cls.component = cls.env.ref("mrp.product_product_computer_desk_head")
        cls.other_component = cls.env.ref("mrp.product_product_computer_desk_leg")
        bom_product_templates = cls.env["mrp.bom"].search([]).product_tmpl_id
        bom_line_products = cls.env["mrp.bom.line"].search([]).product_id
        cls.manual_finished_product = cls.env["product.product"].search(
            [
                ("is_storable", "=", True),
                ("id", "not in", bom_line_products.ids),
                ("product_tmpl_id", "not in", bom_product_templates.ids),
            ],
            limit=1,
        )
        cls.manual_finished_product.write(
            {"categ_id": cls.category.id, "tracking": "lot"}
        )
        cls.finished_product.write({"tracking": "lot"})
        cls.component.write({"categ_id": cls.category.id, "tracking": "lot"})
        cls.other_component.write({"tracking": "lot"})

    @classmethod
    def _create_bom(cls, propagate_fields=True, byproduct_propagate=None):
        byproduct_values = []
        if byproduct_propagate is not None:
            byproduct_values = [
                Command.create(
                    {
                        "product_id": cls.other_component.id,
                        "product_qty": 1.0,
                        "propagate_lot_info": byproduct_propagate,
                    }
                )
            ]
        bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "product_uom_id": cls.finished_product.uom_id.id,
                "type": "normal",
                "byproduct_ids": byproduct_values,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.component.id,
                            "product_qty": 1.0,
                            "product_uom_id": cls.component.uom_id.id,
                        }
                    )
                ],
            }
        )
        if not propagate_fields:
            bom.bom_line_ids.propagate_lot_profile_id = False
        return bom

    @classmethod
    def _create_order(cls, bom):
        with Form(cls.env["mrp.production"]) as form:
            form.product_id = cls.finished_product
            form.bom_id = bom
            form.product_qty = 1.0
            return form.save()

    @classmethod
    def _create_manual_order(cls):
        with Form(cls.env["mrp.production"]) as form:
            form.product_id = cls.manual_finished_product
            form.product_qty = 1.0
            with form.move_raw_ids.new() as move_form:
                move_form.product_id = cls.component
                move_form.product_uom_qty = 1.0
            return form.save()

    @classmethod
    def _create_lot(cls, product, name, ref=False):
        return cls.env["stock.lot"].create(
            {"name": name, "product_id": product.id, "ref": ref}
        )

    @classmethod
    def _update_available_quantity(cls, product, lot, quantity=1.0):
        cls.env["stock.quant"]._update_available_quantity(
            product,
            cls.stock_location,
            quantity,
            lot_id=lot,
        )

    def _prepare_order_to_finish(self, order, source_lot):
        self._update_available_quantity(
            order.bom_id.bom_line_ids.product_id, source_lot
        )
        order.action_confirm()
        order.action_assign()
        move = order.move_raw_ids.filtered(lambda stock_move: stock_move.bom_line_id)
        move.move_line_ids.unlink()
        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": move.product_id.id,
                "product_uom_id": move.product_uom.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "lot_id": source_lot.id,
                "quantity": 1.0,
                "picked": True,
            }
        )
        order.qty_producing = 1.0
        order.lot_producing_id = self._create_lot(
            order.product_id, "FINISHED-LOT", ref=False
        )

    def _prepare_manual_order_to_finish(self, order, source_lot):
        self._update_available_quantity(self.component, source_lot)
        order.action_confirm()
        order.action_assign()
        move = order.move_raw_ids.filtered(lambda stock_move: stock_move.product_id)
        move.move_line_ids.unlink()
        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": move.product_id.id,
                "product_uom_id": move.product_uom.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "lot_id": source_lot.id,
                "quantity": 1.0,
                "picked": True,
            }
        )
        order.qty_producing = 1.0
        order.lot_producing_id = self._create_lot(
            order.product_id, "FINISHED-LOT", ref=False
        )

    def _set_byproduct_lot(self, order, byproduct_lot):
        byproduct_move = order.move_byproduct_ids.filtered(
            lambda move: move.product_id == byproduct_lot.product_id
        )
        byproduct_move.move_line_ids.unlink()
        return self.env["stock.move.line"].create(
            {
                "move_id": byproduct_move.id,
                "product_id": byproduct_move.product_id.id,
                "product_uom_id": byproduct_move.product_uom.id,
                "location_id": byproduct_move.location_id.id,
                "location_dest_id": byproduct_move.location_dest_id.id,
                "lot_id": byproduct_lot.id,
                "quantity": 1.0,
                "picked": True,
            }
        )

    def test_bom_line_gets_default_profile_from_product_category(self):
        with Form(self.env["mrp.bom"]) as bom_form:
            bom_form.product_tmpl_id = self.finished_product.product_tmpl_id
            with bom_form.bom_line_ids.new() as line_form:
                line_form.product_id = self.component
            bom = bom_form.save()
        self.assertEqual(bom.bom_line_ids.propagate_lot_profile_id, self.profile)
        self.assertEqual(bom.bom_line_ids.propagate_lot_field_ids, self.lot_ref_field)

    def test_bom_line_can_override_category_default_profile(self):
        bom = self._create_bom()
        bom.bom_line_ids.propagate_lot_profile_id = False
        self.assertFalse(bom.bom_line_ids.propagate_lot_profile_id)

    def test_only_one_bom_line_can_propagate_lot_info(self):
        bom = self._create_bom()
        with self.assertRaisesRegex(ValidationError, "Only one BoM line"):
            self.env["mrp.bom.line"].create(
                {
                    "bom_id": bom.id,
                    "product_id": self.other_component.id,
                    "product_qty": 1.0,
                    "product_uom_id": self.other_component.uom_id.id,
                    "propagate_lot_profile_id": self.profile.id,
                }
            )

    def test_untracked_bom_line_cannot_propagate_lot_fields(self):
        bom = self._create_bom(propagate_fields=False)
        self.other_component.product_tmpl_id.tracking = "none"
        bom_line = self.env["mrp.bom.line"].create(
            {
                "bom_id": bom.id,
                "product_id": self.other_component.id,
                "product_qty": 1.0,
                "product_uom_id": self.other_component.uom_id.id,
            }
        )
        with self.assertRaisesRegex(ValidationError, "Only tracked components"):
            bom_line.propagate_lot_profile_id = self.profile

    def test_confirm_copies_propagation_data_to_mo(self):
        bom = self._create_bom()
        order = self._create_order(bom)
        order.action_confirm()
        self.assertEqual(order.propagate_lot_bom_line_id, bom.bom_line_ids)
        self.assertEqual(order.propagate_lot_profile_id, self.profile)
        self.assertEqual(order.propagate_lot_field_ids, self.lot_ref_field)

    def test_confirm_manual_mo_uses_finished_product_category_fields(self):
        order = self._create_manual_order()
        order.action_confirm()
        self.assertFalse(order.propagate_lot_bom_line_id)
        self.assertEqual(order.propagate_lot_profile_id, self.profile)
        self.assertEqual(order.propagate_lot_field_ids, self.lot_ref_field)

    def test_confirm_bom_without_propagation_does_not_use_product_category_fields(self):
        bom = self._create_bom(propagate_fields=False)
        order = self._create_order(bom)
        order.action_confirm()
        self.assertFalse(order.propagate_lot_bom_line_id)
        self.assertFalse(order.propagate_lot_profile_id)
        self.assertFalse(order.propagate_lot_field_ids)

    def test_done_propagates_non_empty_lot_field_to_finished_lot(self):
        bom = self._create_bom()
        order = self._create_order(bom)
        source_lot = self._create_lot(self.component, "COMPONENT-LOT", ref="REF-001")
        self._prepare_order_to_finish(order, source_lot)
        order.button_mark_done()
        self.assertEqual(order.lot_producing_id.ref, "REF-001")

    def test_manual_mo_propagates_non_empty_lot_field_to_finished_lot(self):
        order = self._create_manual_order()
        source_lot = self._create_lot(self.component, "COMPONENT-LOT", ref="REF-001")
        self._prepare_manual_order_to_finish(order, source_lot)
        order.button_mark_done()
        self.assertEqual(order.lot_producing_id.ref, "REF-001")

    def test_empty_source_lot_field_is_ignored(self):
        bom = self._create_bom()
        order = self._create_order(bom)
        source_lot = self._create_lot(self.component, "COMPONENT-LOT", ref=False)
        self._prepare_order_to_finish(order, source_lot)
        order.lot_producing_id.ref = "KEEP-ME"
        order.button_mark_done()
        self.assertEqual(order.lot_producing_id.ref, "KEEP-ME")

    def test_done_propagates_lot_field_to_flagged_byproduct_lot(self):
        bom = self._create_bom(byproduct_propagate=True)
        order = self._create_order(bom)
        source_lot = self._create_lot(self.component, "COMPONENT-LOT", ref="REF-001")
        byproduct_lot = self._create_lot(self.other_component, "BYPRODUCT-LOT")
        self._prepare_order_to_finish(order, source_lot)
        self._set_byproduct_lot(order, byproduct_lot)
        order.button_mark_done()
        self.assertEqual(byproduct_lot.ref, "REF-001")

    def test_done_does_not_propagate_lot_field_to_unflagged_byproduct_lot(self):
        bom = self._create_bom(byproduct_propagate=False)
        order = self._create_order(bom)
        source_lot = self._create_lot(self.component, "COMPONENT-LOT", ref="REF-001")
        byproduct_lot = self._create_lot(self.other_component, "BYPRODUCT-LOT")
        self._prepare_order_to_finish(order, source_lot)
        self._set_byproduct_lot(order, byproduct_lot)
        order.button_mark_done()
        self.assertFalse(byproduct_lot.ref)

    def test_multiple_source_lots_raise_clear_error(self):
        bom = self._create_bom()
        order = self._create_order(bom)
        lot_1 = self._create_lot(self.component, "COMPONENT-LOT-1", ref="REF-001")
        lot_2 = self._create_lot(self.component, "COMPONENT-LOT-2", ref="REF-002")
        self._update_available_quantity(self.component, lot_1)
        self._update_available_quantity(self.component, lot_2)
        order.action_confirm()
        move = order.move_raw_ids.filtered(lambda stock_move: stock_move.bom_line_id)
        move.move_line_ids.unlink()
        self.env["stock.move.line"].create(
            [
                {
                    "move_id": move.id,
                    "product_id": self.component.id,
                    "product_uom_id": self.component.uom_id.id,
                    "location_id": move.location_id.id,
                    "location_dest_id": move.location_dest_id.id,
                    "lot_id": lot_1.id,
                    "quantity": 0.5,
                    "picked": True,
                },
                {
                    "move_id": move.id,
                    "product_id": self.component.id,
                    "product_uom_id": self.component.uom_id.id,
                    "location_id": move.location_id.id,
                    "location_dest_id": move.location_dest_id.id,
                    "lot_id": lot_2.id,
                    "quantity": 0.5,
                    "picked": True,
                },
            ]
        )
        order.qty_producing = 1.0
        order.lot_producing_id = self._create_lot(
            order.product_id, "FINISHED-LOT", ref=False
        )
        with self.assertRaisesRegex(UserError, "exactly one consumed lot"):
            order.button_mark_done()

    def test_manual_mo_multiple_source_lots_raise_clear_error(self):
        order = self._create_manual_order()
        lot_1 = self._create_lot(self.component, "COMPONENT-LOT-1", ref="REF-001")
        lot_2 = self._create_lot(self.component, "COMPONENT-LOT-2", ref="REF-002")
        self._update_available_quantity(self.component, lot_1)
        self._update_available_quantity(self.component, lot_2)
        order.action_confirm()
        move = order.move_raw_ids.filtered(lambda stock_move: stock_move.product_id)
        move.move_line_ids.unlink()
        self.env["stock.move.line"].create(
            [
                {
                    "move_id": move.id,
                    "product_id": self.component.id,
                    "product_uom_id": self.component.uom_id.id,
                    "location_id": move.location_id.id,
                    "location_dest_id": move.location_dest_id.id,
                    "lot_id": lot_1.id,
                    "quantity": 0.5,
                    "picked": True,
                },
                {
                    "move_id": move.id,
                    "product_id": self.component.id,
                    "product_uom_id": self.component.uom_id.id,
                    "location_id": move.location_id.id,
                    "location_dest_id": move.location_dest_id.id,
                    "lot_id": lot_2.id,
                    "quantity": 0.5,
                    "picked": True,
                },
            ]
        )
        order.qty_producing = 1.0
        order.lot_producing_id = self._create_lot(
            order.product_id, "FINISHED-LOT", ref=False
        )
        with self.assertRaisesRegex(UserError, "exactly one consumed lot"):
            order.button_mark_done()
