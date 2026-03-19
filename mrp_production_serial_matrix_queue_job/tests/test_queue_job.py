# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase

from odoo.addons.queue_job.tests.common import mock_with_delay


@tagged("-at_install", "post_install")
class TestMrpProductionSerialMatrixQueueJob(TransactionCase):
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

    def test_01_queue_job_chain(self):
        """Test that queue jobs are chained for backorders."""
        production = self._create_mo(3.0)
        matrix = self.matrix_obj.create(
            {
                "production_id": production.id,
            }
        )

        serial_matrix_form = Form(matrix)
        serial_fp_1 = self._create_serial_number(self.final_product, "FP-001", qty=0)
        serial_fp_2 = self._create_serial_number(self.final_product, "FP-002", qty=0)
        serial_matrix_form.finished_lot_ids.add(serial_fp_1)
        serial_matrix_form.finished_lot_ids.add(serial_fp_2)
        serial_matrix = serial_matrix_form.save()

        lines = serial_matrix.line_ids

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

        with mock_with_delay() as (delayable_cls, delayable):
            matrix.button_validate()

            # check 'with_delay()' part:
            self.assertEqual(delayable_cls.call_count, 1)
            # arguments passed in 'with_delay()'
            delay_args, delay_kwargs = delayable_cls.call_args
            self.assertEqual(delay_args, (matrix,))

            # check what's passed to the job method 'cron_actions'
            self.assertEqual(delayable._process_serial_matrix_lot.call_count, 1)
