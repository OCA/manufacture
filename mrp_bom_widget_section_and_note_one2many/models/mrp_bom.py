# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: BADEP
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    # Split bom_line_ids in two fields handled thanks to domain
    # Keep original field bom_line_ids to keep all the native functionnalities
    bom_line_ids = fields.One2many(domain=[("display_type", "=", False)])

    bom_line_with_sectionnote_ids = fields.One2many(
        comodel_name="mrp.bom.line",
        inverse_name="bom_id",
        string="BoM Lines With Sections & Notes",
        copy=False,
    )
