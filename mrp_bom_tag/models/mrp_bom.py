# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    bom_tag_ids = fields.Many2many(
        string="Tags",
        comodel_name="mrp.bom.tag",
        help="Choose or create your tags for your BoM and set its color.",
    )
