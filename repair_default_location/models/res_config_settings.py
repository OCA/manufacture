# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    production_location_id = fields.Many2one(
        related='company_id.repair_production_location_id',
        string="Repair Production Location",
        readonly=False)

    scrap_location_id = fields.Many2one(
        related='company_id.repair_scrap_location_id',
        string="Repair Scrap Location",
        readonly=False)

    use_repair_line_default_location = fields.Boolean(
        string='Use Repair Line Default Source and Destination Location',
        config_parameter='repair.use_repair_line_default_location')
