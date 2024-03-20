# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    # As this field is used on a priority basis, it must be possible to
    # select any type of product concerned
    product_id = fields.Many2one(
        domain="[('type', 'in', ['product', 'consu']),  '|',"
        "('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    # Side effect : if you change product_tmpl_id, it will reset it because
    # of loop of onchange_product_tmpl_id in Odoo code
    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.product_tmpl_id = self.product_id.product_tmpl_id
