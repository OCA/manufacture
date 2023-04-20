# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, exceptions, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_record_components(self):
        self.ensure_one()
        if self._is_subcontract():
            # Try to reserve the components
            for production in self._get_subcontract_production():
                if production.reservation_state != "assigned":
                    production.action_assign()
                    # Block the reception if components could not be reserved
                    # NOTE: this also avoids the creation of negative quants
                    if production.reservation_state != "assigned":
                        raise exceptions.UserError(
                            _("Unable to reserve components in the location %s.")
                            % (production.location_src_id.name)
                        )
        return super().action_record_components()
