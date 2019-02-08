# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def button_mark_done(self):
        """
        Check if picking type option is set.
        If all moves are not done or cancel, block validation.
        :return:
        """
        self.ensure_one()
        if self.picking_type_id.mrp_no_partial:
            # Check only raw moves
            moves = self.move_raw_ids
            current_moves = moves.filtered(
                lambda x:
                float_compare(
                    x.quantity_done,
                    x.product_uom_qty,
                    precision_rounding=x.product_uom.rounding) < 0)
            if current_moves:
                raise ValidationError(
                    _('Please fill in every product quantity in this '
                      'Production Order. You cannot validate a '
                      'Production Order with not done quantities!'))
        return super(MrpProduction, self).button_mark_done()
