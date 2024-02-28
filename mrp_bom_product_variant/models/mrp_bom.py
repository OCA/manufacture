# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    # As this field is used on a priority basis, it must be possible to
    # select any type of product concerned
    product_id = fields.Many2one(
        domain="[('type', 'in', ['product', 'consu'])]",
    )

    # Side effect : if you change product_tmpl_id, it will reset it because
    # of loop of onchange with Odoo code
    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.product_tmpl_id = self.product_id.product_tmpl_id

    # Product product became required
    # We change XML code this way to avoid error with other code and test using view
    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        doc = etree.fromstring(result["arch"])
        nodes = doc.xpath("//field[@name='product_id']")
        if nodes:
            for node in nodes:
                modifiers = json.loads(node.get("modifiers", "{}"))
                modifiers["required"] = True
                node.set("modifiers", json.dumps(modifiers))
            result["arch"] = etree.tostring(doc, encoding="unicode").replace("\t", "")
        return result

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
