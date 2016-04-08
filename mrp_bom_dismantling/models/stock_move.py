# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_consume(self, product_qty, location_id=False,
                       restrict_lot_id=False, restrict_partner_id=False,
                       consumed_for=False):
        """ Override restrict_lot_id if user define one for this move's
        product in wizard.
        """
        # If user define a lot_id for this move's product we override
        restrict_lot_id = self.env.context.get('mapping_move_lot', {}).pop(
            self.id, restrict_lot_id
        )

        return super(StockMove, self).action_consume(
            product_qty, location_id, restrict_lot_id,
            restrict_partner_id, consumed_for
        )
