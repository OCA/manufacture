# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.model
    def _bom_find(self, *args, **kwargs):
        if self.env.context.get("ignore_bom_find"):
            return self.env["mrp.bom"]
        return super()._bom_find(*args, **kwargs)
