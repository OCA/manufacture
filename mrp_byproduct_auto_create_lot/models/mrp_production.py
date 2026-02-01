# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_propagate_lot_setting(self, product):
        return (
            product.propagate_lot_to_byproduct
            or self.company_id.propagate_lot_to_byproduct
        )

    def _set_auto_lot(self):
        """Create and assign lots to by-products in the production order"""
        for production in self:
            propagate_lot_to_byproduct = (
                production._get_propagate_lot_setting(production.product_id) == "yes"
            )
            # Generate lot for the finished product if it's missing
            if (
                propagate_lot_to_byproduct
                and production.product_tracking in ("lot", "serial")
                and not production.lot_producing_id
            ):
                production.action_generate_serial()
            lines = production.mapped("move_byproduct_ids.move_line_ids").filtered(
                lambda x: (
                    not x.lot_id
                    and not x.lot_name
                    and x.product_id.tracking != "none"
                    and x.product_id.auto_create_lot
                )
            )
            for line in lines:
                if propagate_lot_to_byproduct and production.lot_producing_id:
                    line.lot_name = production.lot_producing_id.name
                    continue
                line.lot_name = line._get_lot_sequence()

    def _action_done(self):
        self._set_auto_lot()
        return super()._action_done()

    def button_mark_done(self):
        self._set_auto_lot()
        return super().button_mark_done()
