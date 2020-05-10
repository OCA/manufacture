# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.depends(
        'workorder_ids.state',
        'move_finished_ids',
        'move_finished_ids.quantity_done',
        'is_locked',
    )
    def _get_produced_qty(self):
        """Add workorder_ids.state to depends list."""
        return super()._get_produced_qty()
