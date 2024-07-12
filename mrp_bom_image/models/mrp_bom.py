# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    image_1024 = fields.Binary(related="product_tmpl_id.image_1024")
    image_512 = fields.Binary(related="product_tmpl_id.image_512")
    image_128 = fields.Binary(related="product_tmpl_id.image_128")
