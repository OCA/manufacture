# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.repair.models.repair import Repair


# flake8: noqa: C901
def post_load_hook():
    def action_repair_end_new(self):
        self.write({"repaired": True})
        self.move_id._action_assign()
        self.move_id._action_done()
        for operation in self.operations:
            operation.move_id._action_assign()
            operation.move_id._action_done()
        vals = {"state": "done"}
        if not self.invoice_id and self.invoice_method == "after_repair":
            vals["state"] = "2binvoiced"
        self.write(vals)

    if not hasattr(Repair, "action_repair_end_original"):
        Repair.action_repair_end_original = Repair.action_repair_end
    Repair.action_repair_end = action_repair_end_new
