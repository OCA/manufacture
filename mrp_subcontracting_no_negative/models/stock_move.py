# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, exceptions, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_record_components(self):
        self.ensure_one()
        production = self._get_subcontract_production()[-1:]
        if production.reservation_state != "assigned":
            production.action_assign()
            # Block the reception if components could not be reserved
            # NOTE: this also avoids the creation of negative quants
            if production.reservation_state != "assigned":
                raise exceptions.UserError(
                    _("Unable to reserve components in the location %s.")
                    % (production.location_src_id.name)
                )
        return super()._action_record_components()
