# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResCompany(models.Model):

    _inherit = 'res.company'

    @api.model
    def _default_production_location(self):
        location = self.env['stock.location'].search(
            [('usage', '=', 'production')], limit=1).id
        if location:
            return location
        return False

    @api.model
    def _default_scrap_location(self):
        location = self.env['stock.location'].search(
            [('scrap_location', '=', True)], limit=1).id
        if location:
            return location
        return False

    repair_production_location_id = fields.Many2one(
        'stock.location', 'Production Location',
        default=_default_production_location,
    )
    repair_scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location',
        default=_default_scrap_location,
    )
