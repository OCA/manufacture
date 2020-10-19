# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models

import logging

logger = logging.getLogger(__name__)


class ChangeProductionQty(models.TransientModel):
    _inherit = "change.production.qty"

    @api.multi
    def change_prod_qty(self):
        res = super(ChangeProductionQty, self).change_prod_qty()
        for wizard in self:
            # initial qty (product_uom_qty) cannot be set manually so this is used
            # to avoid removing manual inserted lines
            production = wizard.mo_id
            for move_raw in production.move_raw_ids:
                if not move_raw.bom_line_id and move_raw.product_uom_qty != 0:
                    if move_raw.state == 'draft':
                        move_raw.unlink()
                    elif move_raw.state != 'done':
                        move_raw._action_cancel()
                    else:
                        logger.info('Move %s is already done' % move_raw.id)
        return res
