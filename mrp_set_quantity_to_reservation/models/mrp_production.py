# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_set_quantities_to_reservation(self):
        self.move_raw_ids._set_quantities_to_reservation()
