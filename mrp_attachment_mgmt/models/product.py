# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_see_bom_documents(self):
        first_bom = fields.first(self.bom_ids)
        return first_bom._action_see_bom_documents(self)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_see_bom_documents(self):
        first_bom = fields.first(self.bom_ids)
        return first_bom._action_see_bom_documents(self.product_tmpl_id, self)
