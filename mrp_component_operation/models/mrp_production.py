# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import _, models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    def button_operate_components(self):
        return {
            "name": _("Operate Component"),
            "view_mode": "form",
            "res_model": "mrp.component.operate",
            "view_id": self.env.ref(
                "mrp_component_operation.view_mrp_component_operate_form"
            ).id,
            "type": "ir.actions.act_window",
            "context": {
                "default_mo_id": self.id,
                "product_ids": self.move_raw_ids.move_line_ids.product_id.mapped("id"),
                "lot_ids": self.move_raw_ids.move_line_ids.lot_id.mapped("id"),
                "default_picking_type_id": self.picking_type_id.id,
            },
            "target": "new",
        }
