# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    location_id = fields.Many2one(
        string="Location",
        comodel_name="stock.location",
        compute="_compute_location_id",
        store=True,
        readonly=False,
    )

    @api.depends("picking_type_id")
    def _compute_location_id(self):
        for record in self:
            if record.picking_type_id.default_location_src_id:
                record.location_id = record.picking_type_id.default_location_src_id


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    location_id = fields.Many2one(related="bom_id.location_id", store=True)
