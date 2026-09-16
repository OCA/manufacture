# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models

from odoo.addons.queue_job.job import identity_exact


class MrpProductionSerialMatrix(models.Model):
    _inherit = "mrp.production.serial.matrix"

    def _process_serial_matrix_lot_job_options(
        self, mos, lots_to_process=None, current_mo=False
    ):
        return {
            "identity_key": identity_exact,
            "priority": 15,
            "description": f"MO Production Serial Matrix: ({self.production_id.name})",
        }

    def _register_hook(self):
        self._patch_method(
            "_process_serial_matrix_lot",
            self._patch_job_auto_delay(
                "_process_serial_matrix_lot",
                context_key="auto_delay_process_serial_matrix_lot",
            ),
        )
        return super()._register_hook()

    def call_next_process_serial_matrix_lot(
        self, mos, lots_to_process=None, current_mo=False
    ):
        """
        Override hook to create a new queue_job everytime
        the recursive method is called.
        """
        return self.with_delay()._process_serial_matrix_lot(
            mos, lots_to_process=lots_to_process, current_mo=current_mo
        )

    def button_validate(self):
        return super(
            MrpProductionSerialMatrix,
            self.with_context(auto_delay_process_serial_matrix_lot=True),
        ).button_validate()
