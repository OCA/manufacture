# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def action_replenish(self):
        # The wizard is only necessary if the production route is marked and the product
        # has defined BOMs.
        if (
            self.route_id == self.env.ref("mrp.route_warehouse0_manufacture")
            and self.product_id.bom_ids
        ):
            # In to use the info button, it is necessary to create the wizard
            replenish_wizard = self.env[
                "stock.warehouse.orderpoint.replenish.wizard"
            ].create({"orderpoint_id": self.id})
            replenish_wizard_id = replenish_wizard.id
            return {
                "name": "Replenish",
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "stock.warehouse.orderpoint.replenish.wizard",
                "res_id": replenish_wizard_id,
                "target": "new",
                "context": {"default_orderpoint_id": self.id},
            }
        return super().action_replenish()
