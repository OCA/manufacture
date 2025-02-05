# Copyright 2025 Edilio Escalona Almira - Binhexteam
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class QcInspectionSetTest(models.TransientModel):
    _inherit = "qc.inspection.set.test"

    def action_create_test(self):
        inspection = (
            self.env["qc.inspection"]
            .browse(self.env.context["active_id"])
            .with_context(qc_inspection_set_test=True)
        )
        inspection.test = self.test
        inspection.inspection_lines.unlink()
        inspection.inspection_lines = inspection._prepare_inspection_lines(self.test)
        return True
