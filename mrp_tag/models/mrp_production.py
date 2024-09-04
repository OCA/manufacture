# Copyright 2022 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    tag_ids = fields.Many2many(
        comodel_name="mrp.tag",
        relation="mrp_production_tag_rel",
        column1="mrp_production_id",
        column2="tag_id",
        string="Tags",
    )
