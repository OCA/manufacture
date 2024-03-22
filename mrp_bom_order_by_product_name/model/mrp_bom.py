# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class MrpBom(models.Model):
    _inherit = "mrp.bom"
    # default is _order = "sequence, id"
    # _order = "product_tmpl_id, product_id, code"
    _order = "code"
