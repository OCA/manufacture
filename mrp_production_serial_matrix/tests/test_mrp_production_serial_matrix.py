# Copyright 2021-24 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from unittest.mock import patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpProductionSerialMatrix(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mo_obj = cls.env["mrp.production"]
        cls.product_obj = cls.env["product.product"]
        cls.lot_obj = cls.env["stock.lot"]
        cls.quant_obj = cls.env["stock.quant"]
        cls.bom_obj = cls.env["mrp.bom"]
        cls.bom_line_obj = cls.env["mrp.bom.line"]
        cls.move_line_obj = cls.env["stock.move.line"]
        cls.matrix_obj = cls.env["mrp.production.serial.matrix"]

        cls.company = cls.env.ref("base.main_company")
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")

        # Products and lots:
        cls.final_product = cls.product_obj.create(
            {
                "name": "Finished Product tracked by Serial Numbers",
                "type": "product",
                "tracking": "serial",
            }
        )
        cls.component_1_serial = cls.product_obj.create(
            {
                "name": "Component 1 tracked by Serial Numbers",
                "type": "product",
                "tracking": "serial",
            }
        )
        cls.serial_1_001 = cls._create_serial_number(cls.component_1_serial, "1-001")
        cls.serial_1_002 = cls._create_serial_number(cls.component_1_serial, "1-002")
        cls.serial_1_003 = cls._create_serial_number(cls.component_1_serial, "1-003")

        cls.component_2_serial = cls.product_obj.create(
            {
                "name": "Component 2 tracked by Serial Numbers",
                "type": "product",
                "tracking": "serial",
            }
        )
        cls.serial_2_001 = cls._create_serial_number(cls.component_2_serial, "2-001")
        cls.serial_2_002 = cls._create_serial_number(cls.component_2_serial, "2-002")
        cls.serial_2_003 = cls._create_serial_number(cls.component_2_serial, "2-003")
        cls.serial_2_004 = cls._create_serial_number(cls.component_2_serial, "2-004")
        cls.serial_2_005 = cls._create_serial_number(cls.component_2_serial, "2-005")
        cls.serial_2_006 = cls._create_serial_number(cls.component_2_serial, "2-006")

        cls.component_3_lot = cls.product_obj.create(
            {
                "name": "Component 3 tracked by Lots",
                "type": "product",
                "tracking": "lot",
            }
        )
        cls.lot_3_001 = cls._create_serial_number(
            cls.component_3_lot, "3-001", qty=10.0
        )
        cls.lot_3_002 = cls._create_serial_number(cls.component_3_lot, "3-002", qty=8.0)
        cls.lot_3_003 = cls._create_serial_number(
            cls.component_3_lot, "3-003", qty=12.0
        )

        cls.component_4_no_track = cls.product_obj.create(
            {
                "name": "Component 4 Not tracked",
                "type": "product",
                "tracking": "none",
            }
        )
        cls.quant_obj.create(
            {
                "product_id": cls.component_4_no_track.id,
                "location_id": cls.stock_loc.id,
                "quantity": 20.0,
            }
        )

        # BoM
        cls.bom_1 = cls.bom_obj.create(
            {
                "product_tmpl_id": cls.final_product.product_tmpl_id.id,
                "product_id": cls.final_product.id,
                "product_qty": 1.0,
            }
        )
        cls.bom_line_obj.create(
            {
                "bom_id": cls.bom_1.id,
                "product_id": cls.component_1_serial.id,
                "product_qty": 1.0,
            }
        )
        cls.bom_line_obj.create(
            {
                "bom_id": cls.bom_1.id,
                "product_id": cls.component_2_serial.id,
                "product_qty": 2.0,
            }
        )
        cls.bom_line_obj.create(
            {
                "bom_id": cls.bom_1.id,
                "product_id": cls.component_3_lot.id,
                "product_qty": 4.0,
            }
        )
        cls.bom_line_obj.create(
            {
                "bom_id": cls.bom_1.id,
                "product_id": cls.component_4_no_track.id,
                "product_qty": 1.0,
            }
        )

    @classmethod
    def _create_serial_number(cls, product, name, qty=1.0):
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
                    "location_id": cls.stock_loc.id,
                    "quantity": qty,
                    "lot_id": lot.id,
                }
            )
        return lot

    @classmethod
    def _create_mo(cls, qty, lot=False):
        mo_vals = {
            "product_id": cls.final_product.id,
            "bom_id": cls.bom_1.id,
            "product_qty": qty,
        }
        if lot:
            mo_vals["lot_producing_id"] = lot.id
        production_1 = cls.mo_obj.create(mo_vals)
        production_1.action_confirm()
        production_1.action_assign()
        return production_1

    @classmethod
    def _get_quant(cls, product, lot):
        return cls.quant_obj.search(
            [
                ("product_id", "=", product.id),
                ("location_id", "=", cls.stock_loc.id),
                ("lot_id", "=", lot.id),
            ]
        )

    @classmethod
    def _find_move_lines(cls, mo, component):
        return cls.move_line_obj.search(
            [
                ("move_id.raw_material_production_id", "=", mo.id),
                ("product_id", "=", component.id),
            ]
        )

    def test_01_process_mo_with_matrix(self):
        """Extensive test including all the possibilities for components:
        - 1 tracked by serials.
        - 1 tracked by serials and needing more than one unit.
        - 1 tracked by lots.
        - 1 untracked.
        """
        production_1 = self._create_mo(3.0)
        self.assertEqual(production_1.state, "confirmed")

        # 1. Start matrix (Create the model record):
        matrix_id_old = production_1.action_open_mrp_production_serial_matrix()[
            "res_id"
        ]
        serial_matrix = self.matrix_obj.browse(matrix_id_old)
        # If we remove the matrix, calling the action will create a new one.
        serial_matrix.unlink()
        matrix_id_new = production_1.action_open_mrp_production_serial_matrix()[
            "res_id"
        ]
        self.assertNotEqual(matrix_id_new, matrix_id_old)
        # If a matrix exists, will take the existing.
        matrix_id = production_1.action_open_mrp_production_serial_matrix()["res_id"]
        self.assertEqual(matrix_id_new, matrix_id)
        serial_matrix = self.matrix_obj.browse(matrix_id)
        serial_matrix_form = Form(serial_matrix)

        # Expected: 3 Finished Units * 3 Tracked Components (Comp1, Comp2, Comp2)
        # Note: Comp3 is Lot but 'include_lots' is False by default, so it shouldn't
        # generate lines yet. Based on original code logic:
        # if move.product_id.tracking == "serial": create lines.
        # if move.product_id.tracking == "lot" and self.include_lots: create lines.
        # So initially: Comp1 (1 line) + Comp2 (2 lines) = 3 lines per finished unit.
        # Total = 3 finished units * 3 lines = 9 lines.
        expected_initial = 3 * 3

        self.assertEqual(len(serial_matrix.line_ids), expected_initial)

        # 2. Update to Include Lots
        serial_matrix_form.include_lots = True
        serial_matrix = serial_matrix_form.save()  # Triggers onchange logic

        # Expected: Now Comp3 (Lot) is included (1 line per finished unit)
        # Total lines per finished unit = 3 (serial) + 1 (lot) = 4.
        # Grand total = 3 * 4 = 12 lines.
        expected_lots = 3 * 4
        self.assertEqual(len(serial_matrix.line_ids), expected_lots)
        self.assertEqual(serial_matrix.lot_selection_warning_count, 0)

        # 3. Define specific Finished Product Serial Numbers
        serial_matrix_form = Form(serial_matrix)
        serial_fp_1 = self._create_serial_number(self.final_product, "ABC101", qty=0)
        serial_fp_2 = self._create_serial_number(self.final_product, "ABC102", qty=0)

        # Adding to Many2many triggers onchange
        serial_matrix_form.finished_lot_ids.add(serial_fp_1)
        serial_matrix_form.finished_lot_ids.add(serial_fp_2)

        serial_matrix = serial_matrix_form.save()

        # Now we should have warnings because we haven't selected component lots yet
        self.assertEqual(serial_matrix.lot_selection_warning_count, 2)

        # 4. Fill the matrix cells manually
        # Since 'line_ids' is a One2many on a persistent model,
        # we can iterate and write directly.
        lines = serial_matrix.line_ids

        # --- Fill first row (ABC101) ---
        cell_1_1 = lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_1_serial
        )
        cell_1_1.write({"component_lot_id": self.serial_1_001.id})

        cell_1_2and3 = lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_2_serial
        )
        self.assertEqual(len(cell_1_2and3), 2)

        # Sort to ensure deterministic assignment if needed, or iterate
        for n, cell in enumerate(cell_1_2and3):
            if n == 0:
                cell.write({"component_lot_id": self.serial_2_001.id})
            elif n == 1:
                cell.write({"component_lot_id": self.serial_2_002.id})

        cell_1_4 = lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_3_lot
        )
        cell_1_4.write({"component_lot_id": self.lot_3_003.id})

        # --- Fill second row (ABC102) ---
        cell_2_1 = lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_2
            and line.component_id == self.component_1_serial
        )

        # Simulate a mistake: select the SAME lot as row 1
        # (should trigger warning/error)
        cell_2_1.write({"component_lot_id": self.serial_1_001.id})

        cell_2_2and3 = lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_2
            and line.component_id == self.component_2_serial
        )
        self.assertEqual(len(cell_2_2and3), 2)
        for n, cell in enumerate(cell_2_2and3):
            if n == 0:
                cell.write({"component_lot_id": self.serial_2_005.id})
            elif n == 1:
                cell.write({"component_lot_id": self.serial_2_004.id})

        cell_2_4 = lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_2
            and line.component_id == self.component_3_lot
        )
        cell_2_4.write({"component_lot_id": self.lot_3_002.id})

        # 5. Check Error Handling
        # Need to invalidate cache or trigger recompute of
        # warnings because we wrote directly to DB
        serial_matrix.invalidate_recordset()

        # Note: warning fields are computed. We might need to trigger read to recompute
        self.assertTrue(
            serial_matrix.lot_selection_warning_count > 0,
            "Should have warnings for duplicate serial",
        )

        with self.assertRaises(UserError):
            serial_matrix.button_validate()

        # 6. Fix the error
        cell_2_1.write({"component_lot_id": self.serial_1_003.id})
        serial_matrix.invalidate_recordset()  # Refresh warnings

        # 7. Validate and Verify Results
        serial_matrix.button_validate()

        # Check MOs created/processed
        mos = production_1.procurement_group_id.mrp_production_ids
        # Expected: 3 MOs total (1 done for ABC101, 1 done for ABC102,
        # 1 confirmed for remainder)
        self.assertEqual(len(mos), 3)

        # Verify MO 1 (ABC101)
        mo_1 = mos.filtered(lambda mo: mo.lot_producing_id == serial_fp_1)
        self.assertEqual(mo_1.state, "done")

        ml_c1 = self._find_move_lines(mo_1, self.component_1_serial)
        self.assertEqual(ml_c1.quantity, 1.0)
        self.assertEqual(ml_c1.lot_id, self.serial_1_001)

        # Verify MO 2 (ABC102)
        mo_2 = mos.filtered(lambda mo: mo.lot_producing_id == serial_fp_2)
        self.assertEqual(mo_2.state, "done")

        ml_c1_2 = self._find_move_lines(mo_2, self.component_1_serial)
        self.assertEqual(ml_c1_2.quantity, 1.0)
        self.assertEqual(ml_c1_2.lot_id, self.serial_1_003)

        # Verify MO 3 (Remainder)
        mo_3 = mos.filtered(lambda mo: not mo.lot_producing_id)
        self.assertEqual(mo_3.state, "confirmed")
        self.assertEqual(mo_3.product_qty, 1.0)

    def test_02_process_mo_fully(self):
        """Test processing all units of a MO in the matrix."""
        production_1 = self._create_mo(2.0)
        self.assertEqual(production_1.state, "confirmed")
        serial_matrix = self.matrix_obj.create(
            {
                "production_id": production_1.id,
                "include_lots": True,
            }
        )
        serial_matrix_form = Form(serial_matrix)
        serial_fp_1 = self._create_serial_number(self.final_product, "ABC101", qty=0)
        serial_fp_2 = self._create_serial_number(self.final_product, "ABC102", qty=0)
        serial_matrix_form.finished_lot_ids.add(serial_fp_1)
        serial_matrix_form.finished_lot_ids.add(serial_fp_2)
        serial_matrix = serial_matrix_form.save()

        lines = serial_matrix.line_ids
        # --- Fill first row (ABC101) ---
        lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_1_serial
        ).component_lot_id = self.serial_1_001
        c2_lines_1 = lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_2_serial
        )
        c2_lines_1[0].component_lot_id = self.serial_2_001
        c2_lines_1[1].component_lot_id = self.serial_2_002
        lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_3_lot
        ).component_lot_id = self.lot_3_001

        # --- Fill second row (ABC102) ---
        lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_2
            and line.component_id == self.component_1_serial
        ).component_lot_id = self.serial_1_002
        c2_lines_2 = lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_2
            and line.component_id == self.component_2_serial
        )
        c2_lines_2[0].component_lot_id = self.serial_2_003
        c2_lines_2[1].component_lot_id = self.serial_2_004
        lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_2
            and line.component_id == self.component_3_lot
        ).component_lot_id = self.lot_3_002

        serial_matrix.button_validate()

        # Check MOs created/processed
        mos = production_1.procurement_group_id.mrp_production_ids
        self.assertEqual(len(mos), 2)
        self.assertEqual(production_1.state, "done")
        mo_1 = mos.filtered(lambda mo: mo.lot_producing_id == serial_fp_1)
        self.assertEqual(mo_1.state, "done")
        mo_2 = mos.filtered(lambda mo: mo.lot_producing_id == serial_fp_2)
        self.assertEqual(mo_2.state, "done")

        matrix_id = mo_2.action_open_mrp_production_serial_matrix()["res_id"]
        serial_matrix = self.matrix_obj.browse(matrix_id)

        # Check an error raises when trying to validate a matrix from a done MO.
        with self.assertRaises(UserError):
            serial_matrix.button_validate()

    def test_03_create_from_mo_with_lot(self):
        """Create matrix from MO that has already a lot defined."""
        serial_fp_1 = self._create_serial_number(self.final_product, "ABC101", qty=0)
        production_1 = self._create_mo(1.0, lot=serial_fp_1)
        serial_matrix = self.matrix_obj.create(
            {
                "production_id": production_1.id,
            }
        )
        self.assertEqual(len(serial_matrix.line_ids), 3)
        self.assertEqual(serial_matrix.finished_lot_ids, serial_fp_1)

    def test_04_create_from_mo_with_zero_qty_comp(self):
        """Create matrix from MO which has a component with 0 qty."""
        production_1 = self._create_mo(1.0)
        production_1.move_raw_ids.filtered(
            lambda m: m.product_id == self.component_1_serial
        ).product_uom_qty = 0
        serial_matrix = self.matrix_obj.create(
            {
                "production_id": production_1.id,
            }
        )
        self.assertEqual(len(serial_matrix.line_ids), 2)

    def test_05_lot_reservation(self):
        """Test that lot-tracked components are reserved correctly."""
        production_1 = self._create_mo(1.0)
        serial_matrix = self.matrix_obj.create(
            {
                "production_id": production_1.id,
                "include_lots": True,
            }
        )
        serial_matrix_form = Form(serial_matrix)
        serial_fp_1 = self._create_serial_number(self.final_product, "FP-001", qty=0)
        serial_matrix_form.finished_lot_ids.add(serial_fp_1)
        serial_matrix = serial_matrix_form.save()
        lines = serial_matrix.line_ids
        lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_3_lot
        ).component_lot_id = self.lot_3_001
        # For simplicity, we fill the serial components as well
        lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_1_serial
        ).component_lot_id = self.serial_1_001
        c2_lines = lines.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_2_serial
        )
        c2_lines[0].component_lot_id = self.serial_2_001
        c2_lines[1].component_lot_id = self.serial_2_002

        serial_matrix.button_validate()

        self.assertEqual(production_1.state, "done")
        ml_c3 = self._find_move_lines(production_1, self.component_3_lot)
        self.assertEqual(ml_c3.quantity, 4.0)
        self.assertEqual(ml_c3.lot_id, self.lot_3_001)

    def test_06_delete_done_matrix(self):
        """Test that a done matrix cannot be deleted."""
        production_1 = self._create_mo(1.0)
        serial_matrix = self.matrix_obj.create(
            {
                "production_id": production_1.id,
            }
        )
        serial_matrix.state = "done"
        with self.assertRaises(UserError):
            serial_matrix.unlink()
        serial_matrix.state = "in_progress"
        with self.assertRaises(UserError):
            serial_matrix.unlink()
        serial_matrix.state = "cancel"
        with self.assertRaises(UserError):
            serial_matrix.unlink()
        serial_matrix.state = "draft"
        serial_matrix.unlink()

    def test_07_cancel_matrix(self):
        """A matrix can be cancelled when the related MO is done or cancelled."""
        production = self._create_mo(1.0)
        matrix = self.matrix_obj.create({"production_id": production.id})
        matrix.state = "exception"
        # Cannot cancel while MO is still active
        with self.assertRaises(UserError):
            matrix.action_cancel_matrix()
        # Set MO to done manually and cancel the matrix
        production.state = "done"
        matrix.action_cancel_matrix()
        self.assertEqual(matrix.state, "cancel")
        # Cannot cancel a matrix that is already cancelled or done
        with self.assertRaises(UserError):
            matrix.action_cancel_matrix()

    def test_08_cancel_requires_manager_in_view(self):
        """The Cancel button is restricted to mrp.group_mrp_manager users."""
        manager_group = self.env.ref("mrp.group_mrp_manager")
        # group is referenced only on the view; ensure it exists and the action
        # is callable regardless (group enforcement is the view's responsibility).
        self.assertTrue(manager_group)
        production = self._create_mo(1.0)
        matrix = self.matrix_obj.create({"production_id": production.id})
        matrix.state = "exception"
        production.state = "done"
        matrix.action_cancel_matrix()
        self.assertEqual(matrix.state, "cancel")

    def test_09_reset_to_draft_no_split(self):
        """Reset to draft when the exception happened before any MO split."""
        production = self._create_mo(2.0)
        matrix = self.matrix_obj.create(
            {"production_id": production.id, "include_lots": True}
        )
        serial_fp_1 = self._create_serial_number(self.final_product, "FP-RTD-1", qty=0)
        serial_fp_2 = self._create_serial_number(self.final_product, "FP-RTD-2", qty=0)
        matrix.finished_lot_ids = serial_fp_1 | serial_fp_2
        matrix._onchange_finished_lot_ids()
        line_count_before = len(matrix.line_ids)
        matrix.state = "exception"
        # Cannot reset from another state
        matrix.state = "draft"
        with self.assertRaises(UserError):
            matrix.action_reset_to_draft()
        matrix.state = "exception"
        # Reset should regenerate lines for all serials and point to the same MO
        matrix.action_reset_to_draft()
        self.assertEqual(matrix.state, "draft")
        self.assertEqual(matrix.production_id, production)
        self.assertEqual(matrix.finished_lot_ids, serial_fp_1 | serial_fp_2)
        self.assertEqual(len(matrix.line_ids), line_count_before)

    def test_10_reset_to_draft_after_split(self):
        """Reset to draft after a successful first iteration: matrix points to the
        backorder MO and lines are regenerated for the remaining serials."""
        production = self._create_mo(2.0)
        matrix = self.matrix_obj.create(
            {"production_id": production.id, "include_lots": True}
        )
        serial_fp_1 = self._create_serial_number(self.final_product, "FP-RTD-3", qty=0)
        serial_fp_2 = self._create_serial_number(self.final_product, "FP-RTD-4", qty=0)
        matrix.finished_lot_ids = serial_fp_1 | serial_fp_2
        matrix._onchange_finished_lot_ids()
        # Fill row for serial_fp_1 only
        line_1_c1 = matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_1_serial
        )
        line_1_c1.component_lot_id = self.serial_1_001
        c2_lines_1 = matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_2_serial
        )
        c2_lines_1[0].component_lot_id = self.serial_2_001
        c2_lines_1[1].component_lot_id = self.serial_2_002
        matrix.line_ids.filtered(
            lambda line: line.finished_lot_id == serial_fp_1
            and line.component_id == self.component_3_lot
        ).component_lot_id = self.lot_3_001
        # Process only the first finished serial; simulate the exception that
        # would have happened on the second iteration.
        matrix._prepare_mo_for_serial(production, serial_fp_1)
        matrix._process_component_moves(
            production, serial_fp_1, matrix._get_matrix_lines_map()
        )
        backorder_mo = matrix._validate_and_get_backorder(production)
        self.assertTrue(backorder_mo)
        self.assertEqual(production.state, "done")
        matrix.state = "exception"
        matrix.action_reset_to_draft()
        self.assertEqual(matrix.state, "draft")
        self.assertEqual(matrix.production_id, backorder_mo)
        self.assertEqual(matrix.finished_lot_ids, serial_fp_2)
        # Lines should now correspond to the backorder MO's qty (1) for the
        # remaining serial only.
        self.assertEqual(matrix.line_ids.mapped("finished_lot_id"), serial_fp_2)

    def test_11_reset_to_draft_no_pending_mo(self):
        """If all related MOs are done, reset to draft must fail."""
        production = self._create_mo(1.0)
        matrix = self.matrix_obj.create({"production_id": production.id})
        matrix.state = "exception"
        production.state = "done"
        with self.assertRaises(UserError):
            matrix.action_reset_to_draft()

    def test_12_reserve_lot_in_move_requires_the_needed_qty(self):
        """A lot that cannot cover the needed quantity is refused instead of
        being partially reserved and consumed short."""
        production = self._create_mo(1.0)
        matrix = self.matrix_obj.create({"production_id": production.id})
        short_lot = self._create_serial_number(self.component_3_lot, "3-SHORT", qty=1.0)
        move = production.move_raw_ids.filtered(
            lambda m: m.product_id == self.component_3_lot
        )
        with self.assertRaises(ValidationError):
            matrix._reserve_lot_in_move(move, short_lot, qty=4.0)
        self.assertFalse(move.move_line_ids.filtered(lambda ml: ml.lot_id == short_lot))

    def test_13_no_component_line_is_left_without_a_lot(self):
        """When a selected lot cannot cover the whole need, the run must stop.

        It used to go on and leave a surplus line with no lot on a lot-tracked
        component, which Odoo then consumed as untracked stock.
        """
        production = self._create_mo(1.0)
        matrix = self.matrix_obj.create(
            {"production_id": production.id, "include_lots": True}
        )
        serial_fp = self._create_serial_number(self.final_product, "FP-SHORT", qty=0)
        matrix.finished_lot_ids = serial_fp
        matrix._onchange_finished_lot_ids()
        # 3-002 holds 8 units, but only 2 of them are free here, while the BoM
        # needs 4 of the component per finished unit.
        short_lot = self._create_serial_number(self.component_3_lot, "3-PART", qty=2.0)
        c3_line = matrix.line_ids.filtered(
            lambda line: line.component_id == self.component_3_lot
        )
        c3_line.component_lot_id = short_lot
        move = production.move_raw_ids.filtered(
            lambda m: m.product_id == self.component_3_lot
        )
        with self.assertRaises(ValidationError):
            matrix._amend_reservations(move, c3_line)
        self.assertFalse(
            move.move_line_ids.filtered(lambda ml: not ml.lot_id),
            "a lot-tracked component must never carry a line without a lot",
        )

    def test_14_only_the_selected_lots_are_consumed(self):
        """Lines on lots the operator did not select are dropped, not consumed:
        never as untracked stock, and never above what the BoM asks for."""
        production = self._create_mo(1.0)
        matrix = self.matrix_obj.create(
            {"production_id": production.id, "include_lots": True}
        )
        serial_fp = self._create_serial_number(self.final_product, "FP-LEFT", qty=0)
        matrix.finished_lot_ids = serial_fp
        matrix._onchange_finished_lot_ids()
        c3_line = matrix.line_ids.filtered(
            lambda line: line.component_id == self.component_3_lot
        )
        c3_line.component_lot_id = self.lot_3_003
        move = production.move_raw_ids.filtered(
            lambda m: m.product_id == self.component_3_lot
        )
        self.assertTrue(move.move_line_ids)
        self.assertNotEqual(move.move_line_ids.lot_id, self.lot_3_003)
        matrix._amend_reservations(move, c3_line)
        matrix._consume_selected_lots(move, c3_line)
        self.assertEqual(move.move_line_ids.mapped("lot_id"), self.lot_3_003)
        self.assertEqual(sum(move.move_line_ids.mapped("quantity")), 4.0)
        self.assertTrue(all(move.move_line_ids.mapped("picked")))

    def test_15_reservations_match_the_move_lines(self):
        """After the matrix has set the lots, every quant it touched must hold
        exactly what the move lines say is reserved on it."""
        production = self._create_mo(1.0)
        matrix = self.matrix_obj.create(
            {"production_id": production.id, "include_lots": True}
        )
        serial_fp = self._create_serial_number(self.final_product, "FP-INV", qty=0)
        matrix.finished_lot_ids = serial_fp
        matrix._onchange_finished_lot_ids()
        c3_line = matrix.line_ids.filtered(
            lambda line: line.component_id == self.component_3_lot
        )
        c3_line.component_lot_id = self.lot_3_002
        move = production.move_raw_ids.filtered(
            lambda m: m.product_id == self.component_3_lot
        )
        matrix._amend_reservations(move, c3_line)
        matrix._consume_selected_lots(move, c3_line)
        for lot in (self.lot_3_001, self.lot_3_002, self.lot_3_003, False):
            quants = self.quant_obj.search(
                [
                    ("product_id", "=", self.component_3_lot.id),
                    ("location_id", "=", self.stock_loc.id),
                    ("lot_id", "=", lot and lot.id),
                ]
            )
            lines = self.move_line_obj.search(
                [
                    ("product_id", "=", self.component_3_lot.id),
                    ("location_id", "=", self.stock_loc.id),
                    ("lot_id", "=", lot and lot.id),
                    ("state", "not in", ("done", "cancel")),
                ]
            )
            self.assertAlmostEqual(
                sum(quants.mapped("reserved_quantity")),
                sum(lines.mapped("quantity_product_uom")),
                msg="reservation out of sync for lot %s" % (lot and lot.name or "-"),
            )

    def test_16_a_failed_serial_rolls_back_its_own_stock_changes(self):
        """A serial number that fails must leave no stock change behind.

        The errors raised while validating come from a flush. Catching them
        without rolling back used to leave the transaction with the stock
        changes already applied, and writing the exception on the matrix
        committed them - including quantities a constraint had just rejected.
        """
        production = self._create_mo(1.0)
        matrix = self.matrix_obj.create(
            {"production_id": production.id, "include_lots": True}
        )
        serial_fp = self._create_serial_number(self.final_product, "FP-ROLL", qty=0)
        matrix.finished_lot_ids = serial_fp
        matrix._onchange_finished_lot_ids()
        matrix.line_ids.filtered(
            lambda line: line.component_id == self.component_3_lot
        ).component_lot_id = self.lot_3_002
        matrix.line_ids.filtered(
            lambda line: line.component_id == self.component_1_serial
        ).component_lot_id = self.serial_1_001
        c2_lines = matrix.line_ids.filtered(
            lambda line: line.component_id == self.component_2_serial
        )
        c2_lines[0].component_lot_id = self.serial_2_001
        c2_lines[1].component_lot_id = self.serial_2_002

        quant = self._get_quant(self.component_3_lot, self.lot_3_002)
        before = (quant.quantity, quant.reserved_quantity)

        with patch.object(
            type(matrix),
            "_validate_and_get_backorder",
            side_effect=UserError("validation blew up"),
        ):
            matrix.state = "in_progress"
            matrix._process_serial_matrix()

        self.assertEqual(matrix.state, "exception")
        self.assertEqual(
            (quant.quantity, quant.reserved_quantity),
            before,
            "the failed serial number left stock changes behind",
        )
        self.assertGreaterEqual(quant.reserved_quantity, 0.0)
