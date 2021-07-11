# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class RepairLine(models.Model):

    _inherit = 'repair.line'

    @api.onchange('type', 'repair_id')
    def onchange_operation_type(self):
        super().onchange_operation_type()
        if self.env['ir.config_parameter'].sudo().get_param(
                'repair.use_repair_line_default_location'):
            production_location = (
                self.repair_id.company_id.repair_production_location_id
            )
            scrap_location = (
                self.repair_id.company_id.repair_scrap_location_id
            )
            if self.type:
                if self.type == 'add' and production_location:
                    self.location_dest_id = production_location
                else:
                    if production_location:
                        self.location_id = production_location
                    if scrap_location:
                        self.location_dest_id = scrap_location
