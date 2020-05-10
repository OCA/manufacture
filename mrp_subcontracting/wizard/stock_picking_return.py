# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import models


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = super()._prepare_move_default_values(return_line, new_picking)
        vals['is_subcontract'] = False
        if return_line.move_id.is_subcontract:
            vals['location_dest_id'] = return_line.move_id.location_id.id
        return vals
