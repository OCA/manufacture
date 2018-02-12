# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    location_id = fields.Many2one(
        related='picking_type_id.default_location_dest_id',
        store=True,
    )


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    location_id = fields.Many2one(
        related='bom_id.picking_type_id.default_location_src_id',
        store=True,
    )
