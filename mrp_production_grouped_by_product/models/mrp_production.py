# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, vals):
        if not self._context.get('merge_products_into_mo'):
            return super(MrpProduction, self).create(vals)
        # We return the MO to merge into
        return self._context.get('merge_products_into_mo')
