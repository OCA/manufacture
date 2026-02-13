# Copyright 2021-24 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import UserError
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
        serial_matrix.state = "draft"
        serial_matrix.unlink()
