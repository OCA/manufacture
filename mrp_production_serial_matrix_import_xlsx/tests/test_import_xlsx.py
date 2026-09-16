# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
import io

import xlsxwriter

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestMrpProductionSerialMatrixImportXlsx(TransactionCase):
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

    def test_01_import_xlsx(self):
        """Test importing an XLSX file to fill the matrix."""
        production = self._create_mo(2.0)
        matrix = self.matrix_obj.create(
            {
                "production_id": production.id,
                "include_lots": True,
            }
        )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Template")

        headers = [
            "Finished Product Serial Numbers",
            "Component 1 tracked by Serial Numbers (1)",
            "Component 2 tracked by Serial Numbers (1)",
            "Component 2 tracked by Serial Numbers (2)",
            "Component 3 tracked by Lots",
        ]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        data = [
            ["FP-001", "1-001", "2-001", "2-002", "3-001"],
            ["FP-002", "1-002", "2-003", "2-004", "3-002"],
        ]
        for row_num, row_data in enumerate(data, start=1):
            for col_num, cell_data in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_data)

        workbook.close()
        output.seek(0)
        file_data = base64.encodebytes(output.getvalue())
        output.close()

        matrix.write(
            {
                "import_file": file_data,
                "import_filename": "test.xlsx",
            }
        )

        matrix.action_import_template()

        self.assertEqual(len(matrix.line_ids), 8)
        self.assertEqual(len(matrix.finished_lot_ids), 2)

        line_fp1_c1 = matrix.line_ids.filtered(
            lambda line: line.finished_lot_name == "FP-001"
            and line.component_id == self.component_1_serial
        )
        self.assertEqual(line_fp1_c1.component_lot_id, self.serial_1_001)

        line_fp2_c3 = matrix.line_ids.filtered(
            lambda line: line.finished_lot_name == "FP-002"
            and line.component_id == self.component_3_lot
        )
        self.assertEqual(line_fp2_c3.component_lot_id, self.lot_3_002)

    def test_02_import_xlsx_extra_cols(self):
        """Test importing an XLSX file with extra columns."""
        production = self._create_mo(1.0)
        matrix = self.matrix_obj.create(
            {
                "production_id": production.id,
                "include_lots": True,
            }
        )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Template")

        headers = [
            "Finished Product Serial Numbers",
            "Component 1 tracked by Serial Numbers (1)",
            "Extra Column",
            "Component 3 tracked by Lots",
        ]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        data = [
            ["FP-001", "1-001", "extra_data", "3-001"],
        ]
        for row_num, row_data in enumerate(data, start=1):
            for col_num, cell_data in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_data)

        workbook.close()
        output.seek(0)
        file_data = base64.encodebytes(output.getvalue())
        output.close()

        matrix.write(
            {
                "import_file": file_data,
                "import_filename": "test.xlsx",
            }
        )

        matrix.action_import_template()
        self.assertEqual(len(matrix.line_ids), 4)
        line_fp1_c1 = matrix.line_ids.filtered(
            lambda line: line.finished_lot_name == "FP-001"
            and line.component_id == self.component_1_serial
        )
        self.assertEqual(line_fp1_c1.component_lot_id, self.serial_1_001)
        line_fp1_c3 = matrix.line_ids.filtered(
            lambda line: line.finished_lot_name == "FP-001"
            and line.component_id == self.component_3_lot
        )
        self.assertEqual(line_fp1_c3.component_lot_id, self.lot_3_001)

    def test_03_import_xlsx_missing_lot(self):
        """Test importing an XLSX file with a missing component lot."""
        production = self._create_mo(1.0)
        matrix = self.matrix_obj.create(
            {
                "production_id": production.id,
                "include_lots": True,
            }
        )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Template")

        headers = [
            "Finished Product Serial Numbers",
            "Component 1 tracked by Serial Numbers (1)",
        ]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        data = [
            ["FP-001", "MISSING-LOT"],
        ]
        for row_num, row_data in enumerate(data, start=1):
            for col_num, cell_data in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_data)

        workbook.close()
        output.seek(0)
        file_data = base64.encodebytes(output.getvalue())
        output.close()

        matrix.write(
            {
                "import_file": file_data,
                "import_filename": "test.xlsx",
            }
        )

        with self.assertRaises(UserError):
            matrix.action_import_template()
