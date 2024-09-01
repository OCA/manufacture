# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    repair_id = fields.Many2one("repair.order")

    def action_create_repair_order(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "repair.action_repair_order_form"
        )
        action["view_mode"] = "form"
        action["views"] = [(False, "form")]
        action["target"] = "new"
        action["name"] = _("Create Repair Order")

        action["context"] = {
            "default_product_id": self.product_id.id,
            "default_product_qty": self.product_qty,
            "default_mrp_ids": [self.id],
        }
        return action

    def action_view_mrp_production_repair_orders(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "repair.order",
            "res_id": self.repair_id.id,
        }
