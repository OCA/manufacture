# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    location_id = fields.Many2one(string="Location", comodel_name="stock.location")

    @api.onchange("picking_type_id")
    def _onchange_picking_type_id(self):
        if self.picking_type_id and self.picking_type_id.default_location_src_id:
            self.location_id = self.picking_type_id.default_location_src_id


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    location_id = fields.Many2one(related="bom_id.location_id", store=True)
