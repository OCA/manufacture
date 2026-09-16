# Copyright 2026 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpProductionSerialMatrixSubcontracting(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Bypass queue_job in case mrp_production_serial_matrix_queue_job is installed
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        cls.product_obj = cls.env["product.product"]
        cls.lot_obj = cls.env["stock.lot"]
        cls.quant_obj = cls.env["stock.quant"]
        cls.bom_obj = cls.env["mrp.bom"]
        cls.matrix_obj = cls.env["mrp.production.serial.matrix"]
        cls.move_line_obj = cls.env["stock.move.line"]

        cls.company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.subcontract_location = cls.company.subcontracting_location_id

        # Subcontractor
        cls.subcontractor = cls.env["res.partner"].create(
            {
                "name": "Subcontractor",
                "company_id": cls.company.id,
            }
        )

        # Finished product (tracked by serial)
        cls.finished = cls.product_obj.create(
            {
                "name": "Finished Subcontracted",
                "type": "product",
                "tracking": "serial",
            }
        )
        # Components
        cls.comp_serial = cls.product_obj.create(
            {
                "name": "Serial-tracked component",
                "type": "product",
                "tracking": "serial",
            }
        )
        cls.comp_lot = cls.product_obj.create(
            {
                "name": "Lot-tracked component",
                "type": "product",
                "tracking": "lot",
            }
        )
        # Subcontracting BoM
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.product_tmpl_id = cls.finished.product_tmpl_id
        bom_form.product_qty = 1.0
        bom_form.type = "subcontract"
        bom_form.consumption = "strict"
        bom_form.subcontractor_ids.add(cls.subcontractor)
        with bom_form.bom_line_ids.new() as line:
            line.product_id = cls.comp_serial
            line.product_qty = 1.0
        with bom_form.bom_line_ids.new() as line:
            line.product_id = cls.comp_lot
            line.product_qty = 2.0
        cls.bom = bom_form.save()

        # Component lots/serials physically at the subcontracting location
        cls.serial_a = cls._create_serial(cls.comp_serial, "S-A", 1.0)
        cls.serial_b = cls._create_serial(cls.comp_serial, "S-B", 1.0)
        cls.lot_x = cls._create_serial(cls.comp_lot, "L-X", 5.0)

        # Finished product lots
        cls.fp_serial_1 = cls._create_serial(cls.finished, "FP-001", 0.0)
        cls.fp_serial_2 = cls._create_serial(cls.finished, "FP-002", 0.0)

    @classmethod
    def _create_serial(cls, product, name, qty, location=None):
        location = location or cls.subcontract_location
        lot = cls.lot_obj.create(
            {
                "product_id": product.id,
                "name": name,
                "company_id": cls.company.id,
            }
        )
        if qty > 0:
            cls.quant_obj.create(
                {
                    "product_id": product.id,
                    "location_id": location.id,
                    "quantity": qty,
                    "lot_id": lot.id,
                }
            )
        return lot

    def _create_subcontract_receipt(self, qty):
        picking_form = Form(self.env["stock.picking"])
        picking_form.picking_type_id = self.warehouse.in_type_id
        picking_form.partner_id = self.subcontractor
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.finished
            move.product_uom_qty = qty
        picking = picking_form.save()
        picking.action_confirm()
        return picking

    def test_01_button_visible_only_on_subcontract_receipt(self):
        """The Serial Matrix button is only visible when there is a subcontracted
        MO with a serial-tracked product on the receipt."""
        picking = self._create_subcontract_receipt(2.0)
        self.assertTrue(picking.show_subcontract_serial_matrix)
        # Plain receipt with non-tracked product should not show the button
        plain_product = self.product_obj.create({"name": "Plain", "type": "product"})
        picking_form = Form(self.env["stock.picking"])
        picking_form.picking_type_id = self.warehouse.in_type_id
        picking_form.partner_id = self.subcontractor
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = plain_product
            move.product_uom_qty = 1
        plain_picking = picking_form.save()
        plain_picking.action_confirm()
        self.assertFalse(plain_picking.show_subcontract_serial_matrix)

    def test_02_open_matrix_creates_one_per_subcontract_mo(self):
        """Opening the matrix from the receipt creates a matrix for each
        subcontracted MO and opens the form view when only one exists."""
        picking = self._create_subcontract_receipt(2.0)
        action = picking.action_open_subcontract_serial_matrix()
        self.assertEqual(action["res_model"], "mrp.production.serial.matrix")
        self.assertIn("res_id", action)
        matrix = self.matrix_obj.browse(action["res_id"])
        mo = picking.move_ids._get_subcontract_production()
        self.assertEqual(matrix.production_id, mo)
        # Re-opening returns the same matrix
        action2 = picking.action_open_subcontract_serial_matrix()
        self.assertEqual(action2["res_id"], action["res_id"])

    def test_03_validate_matrix_records_subcontract_mos(self):
        """Validating the matrix should record each subcontracted MO via the
        subcontracting flow and split into backorders correctly."""
        picking = self._create_subcontract_receipt(2.0)
        mo = picking.move_ids._get_subcontract_production()
        self.assertEqual(mo.product_qty, 2.0)
        # Open the matrix from the picking
        action = picking.action_open_subcontract_serial_matrix()
        matrix = self.matrix_obj.browse(action["res_id"])
        # Pick finished serials
        matrix_form = Form(matrix)
        matrix_form.include_lots = True
        matrix_form.finished_lot_ids.add(self.fp_serial_1)
        matrix_form.finished_lot_ids.add(self.fp_serial_2)
        matrix = matrix_form.save()
        # Fill component lots/serials
        # Row 1: FP-001 -> S-A, L-X
        line_1_serial = matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == self.fp_serial_1
            and line.component_id == self.comp_serial
        )
        line_1_serial.component_lot_id = self.serial_a
        line_1_lot = matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == self.fp_serial_1
            and line.component_id == self.comp_lot
        )
        line_1_lot.component_lot_id = self.lot_x
        # Row 2: FP-002 -> S-B, L-X
        line_2_serial = matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == self.fp_serial_2
            and line.component_id == self.comp_serial
        )
        line_2_serial.component_lot_id = self.serial_b
        line_2_lot = matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == self.fp_serial_2
            and line.component_id == self.comp_lot
        )
        line_2_lot.component_lot_id = self.lot_x
        # Validate
        matrix.button_validate()
        self.assertEqual(matrix.state, "done")
        # Both subcontracted MOs should be recorded
        mos = mo.procurement_group_id.mrp_production_ids
        self.assertEqual(len(mos), 2)
        for production in mos:
            self.assertTrue(production.subcontracting_has_been_recorded)
            self.assertIn(
                production.lot_producing_id, self.fp_serial_1 | self.fp_serial_2
            )
        # Validate the receipt to finalize the subcontracting flow
        picking.move_ids.picked = True
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        for production in mos:
            self.assertEqual(production.state, "done")

    def test_04_validate_matrix_partial_creates_backorder_mo(self):
        """If the matrix is validated for fewer finished serials than the MO
        demand, a subcontracted backorder MO should remain pending."""
        picking = self._create_subcontract_receipt(3.0)
        mo = picking.move_ids._get_subcontract_production()
        action = picking.action_open_subcontract_serial_matrix()
        matrix = self.matrix_obj.browse(action["res_id"])
        matrix_form = Form(matrix)
        matrix_form.include_lots = True
        matrix_form.finished_lot_ids.add(self.fp_serial_1)
        matrix = matrix_form.save()
        matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == self.fp_serial_1
            and line.component_id == self.comp_serial
        ).component_lot_id = self.serial_a
        matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == self.fp_serial_1
            and line.component_id == self.comp_lot
        ).component_lot_id = self.lot_x
        matrix.button_validate()
        mos = mo.procurement_group_id.mrp_production_ids
        # 1 recorded + 1 backorder (still pending)
        self.assertEqual(len(mos), 2)
        recorded = mos.filtered(lambda m: m.subcontracting_has_been_recorded)
        pending = mos - recorded
        self.assertEqual(len(recorded), 1)
        self.assertEqual(recorded.lot_producing_id, self.fp_serial_1)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending.product_qty, 2.0)

    def test_05_notifies_user_on_completion(self):
        """When the matrix finishes, a message notifying the launching user is
        posted on the subcontracting receipt."""
        picking = self._create_subcontract_receipt(2.0)
        action = picking.action_open_subcontract_serial_matrix()
        matrix = self.matrix_obj.browse(action["res_id"])
        matrix_form = Form(matrix)
        matrix_form.include_lots = True
        matrix_form.finished_lot_ids.add(self.fp_serial_1)
        matrix_form.finished_lot_ids.add(self.fp_serial_2)
        matrix = matrix_form.save()
        matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == self.fp_serial_1
            and line.component_id == self.comp_serial
        ).component_lot_id = self.serial_a
        matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == self.fp_serial_1
            and line.component_id == self.comp_lot
        ).component_lot_id = self.lot_x
        matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == self.fp_serial_2
            and line.component_id == self.comp_serial
        ).component_lot_id = self.serial_b
        matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == self.fp_serial_2
            and line.component_id == self.comp_lot
        ).component_lot_id = self.lot_x
        messages_before = picking.message_ids
        matrix.button_validate()
        self.assertEqual(matrix.state, "done")
        new_messages = picking.message_ids - messages_before
        self.assertTrue(new_messages)
        completion_msg = new_messages.filtered(
            lambda m: self.env.user.partner_id in m.partner_ids
        )
        self.assertTrue(
            completion_msg,
            "A completion message notifying the launching user should be posted "
            "on the receipt.",
        )
        self.assertIn("finished", completion_msg[0].body)

    def test_06_completion_message_targets_launching_receipt(self):
        """The completion message is posted on the receipt the matrix was
        launched from, even when the subcontract move spans several pickings
        (e.g. the goods were received through a backorder)."""
        picking = self._create_subcontract_receipt(2.0)
        action = picking.action_open_subcontract_serial_matrix()
        matrix = self.matrix_obj.browse(action["res_id"])
        self.assertEqual(matrix.subcontract_receipt_picking_id, picking)
        self.assertEqual(matrix._get_subcontract_receipt_picking(), picking)
        # Even if the production's subcontract move now points to another
        # (earlier) picking, the stored launching receipt must win.
        other_picking = self._create_subcontract_receipt(1.0)
        matrix.subcontract_receipt_picking_id = other_picking
        self.assertEqual(matrix._get_subcontract_receipt_picking(), other_picking)
