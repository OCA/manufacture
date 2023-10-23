# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, models


class MrpWorkOrderLine(models.Model):
    _inherit = "mrp.workorder.line"

    def action_new_line_wizard(self):
        return {
            "name": _("Create new Component Line"),
            "view_mode": "form",
            "res_model": "mrp.workorder.new.line",
            "view_id": self.env.ref(
                "mrp_workorder_update_component.view_mrp_workorder_new_line_form"
            ).id,
            "type": "ir.actions.act_window",
            "context": {
                "default_workorder_id": self.raw_workorder_id.id,
                "default_workorder_line_id": self.id,
                "default_product_id": self.product_id.id,
                "default_original_line_qty": self.qty_to_consume,
                "default_company_id": self.company_id.id,
            },
            "target": "new",
        }
