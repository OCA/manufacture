# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class MrpProductProduce(models.TransientModel):

    _inherit = 'mrp.product.produce'

    @api.multi
    def do_produce(self):
        if self.production_id.picking_type_id.mrp_no_partial:
            incomplete_move_lots = self.consume_line_ids.filtered(
                lambda l: float_compare(
                    l.quantity,
                    l.quantity_done,
                    precision_rounding=l.product_id.uom_id.rounding))
            if incomplete_move_lots:
                raise ValidationError(
                    _('Please fill in every lot quantity for this '
                      'Production Order. You cannot validate a '
                      'Production Order with not done quantities!'))
        return super(MrpProductProduce, self).do_produce()
