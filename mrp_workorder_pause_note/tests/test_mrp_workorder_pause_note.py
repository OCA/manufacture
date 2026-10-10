# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.base.tests.common import BaseCommon


class TestMrpWorkorderPauseNote(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.workcenter = cls.env["mrp.workcenter"].create({"name": "Test Workcenter"})

    def _create_workorder(self, name="Test Product"):
        product = self.env["product.product"].create(
            {"name": name, "is_storable": True}
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "operation_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Operation",
                            "workcenter_id": self.workcenter.id,
                            "time_cycle_manual": 10,
                        },
                    )
                ],
            }
        )
        production = self.env["mrp.production"].create(
            {"product_id": product.id, "bom_id": bom.id, "product_qty": 1.0}
        )
        production.action_confirm()
        return production.workorder_ids

    def setUp(self):
        super().setUp()
        self.workorder = self._create_workorder()

    def test_last_pause_note_empty_before_any_pause(self):
        self.workorder.button_start()
        self.assertFalse(self.workorder.last_pause_note)
        self.assertFalse(self.workorder.last_pause_note_user_id)

    def test_last_pause_note_reflects_last_closed_segment(self):
        self.workorder.button_start()
        open_time = self.workorder.time_ids.filtered(lambda t: not t.date_end)
        open_time.pause_note = "First note"
        self.workorder.with_context(
            mrp_wo_skip_pause_note_request=True
        ).button_pending()

        self.workorder.invalidate_recordset()
        self.assertEqual(self.workorder.last_pause_note, "First note")
        self.assertEqual(self.workorder.last_pause_note_user_id, self.env.user)

    def test_button_pending_skips_wizard_with_context_flag(self):
        self.workorder.button_start()
        result = self.workorder.with_context(
            mrp_wo_skip_pause_note_request=True
        ).button_pending()
        self.assertFalse(result)
        self.assertFalse(self.workorder.time_ids.filtered(lambda t: not t.date_end))

    def test_button_pending_skips_wizard_for_multiple_workorders(self):
        workorder2 = self._create_workorder("Test Product 2")
        self.workorder.button_start()
        workorder2.button_start()
        combined = self.workorder | workorder2

        result = combined.button_pending()

        self.assertFalse(result)

    def test_wizard_action_confirm_writes_note_and_pauses_workorder(self):
        self.workorder.button_start()
        wizard = self.env["mrp.workorder.pause.note.wizard"].create(
            {
                "workorder_id": self.workorder.id,
                "note": "Careful with part X",
            }
        )

        wizard.action_confirm()

        closed_time = self.workorder.time_ids.filtered(lambda t: t.date_end)
        self.assertEqual(closed_time.pause_note, "Careful with part X")
        self.assertFalse(self.workorder.time_ids.filtered(lambda t: not t.date_end))
