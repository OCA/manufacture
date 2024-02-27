# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    # Product product became mandatory by the view and not by the python code
    # so as not to interfere with other codes
    product_id = fields.Many2one(
        "product.product",
        "Product Variant",
        domain="[('type', 'in', ['product', 'consu'])]",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.product_tmpl_id = self.product_id.product_tmpl_id

    @api.onchange("product_tmpl_id")
    def _onchange_product_tmpl_id(self):
        self.product_id = self.product_tmpl_id.product_variant_ids[0]

    # Mandatory with this module but prevent warning for demo datas
    # of other modules
    @api.constrains(
        "product_id",
        "product_tmpl_id",
    )
    def _check_product_and_variant(self):
        for bom in self.filtered(lambda x: x.product_id):
            if bom.product_id.product_tmpl_id != bom.product_tmpl_id:
                raise ValidationError(
                    _(
                        "In BoM, product Variant and product Template"
                        " should be set and linked."
                    )
                )
