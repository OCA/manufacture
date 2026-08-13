# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _needs_bom_selection_wizard(self):
        """The wizard only makes sense for a manually triggered orderpoint whose
        effective route manufactures the product and that has candidate bills of
        materials to choose from.

        Auto-triggered orderpoints are excluded on purpose: their `qty_to_order`
        is always the computed one (see `_inverse_qty_to_order`), so the
        quantities entered in the wizard would be silently discarded.
        """
        self.ensure_one()
        return (
            self.show_bom
            and self.trigger == "manual"
            and bool(self._get_selectable_boms())
        )

    def _get_selectable_boms(self):
        """Bills of materials that can be used to manufacture this product."""
        self.ensure_one()
        return self.product_id.bom_ids.filtered(
            lambda x: x.type == "normal"
            and (not x.product_id or x.product_id == self.product_id)
            and (not x.company_id or x.company_id == self.company_id)
        )

    def action_replenish(self, force_to_max=False):
        if len(self) == 1 and self._needs_bom_selection_wizard():
            if force_to_max:
                # Same behavior as the core "Order To Max" entry, but letting
                # the user split that quantity among the different BoMs.
                self.qty_to_order = self._get_multiple_rounded_qty(
                    self.product_max_qty - self.qty_forecast
                )
            # The wizard record has to exist beforehand so that the raw material
            # availability button can navigate back to it.
            replenish_wizard = self.env[
                "stock.warehouse.orderpoint.replenish.wizard"
            ].create({"orderpoint_id": self.id})
            return {
                "name": self.env._("Replenish"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "stock.warehouse.orderpoint.replenish.wizard",
                "res_id": replenish_wizard.id,
                "target": "new",
                "context": {"default_orderpoint_id": self.id},
            }
        return super().action_replenish(force_to_max=force_to_max)
