from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    nested_product_template_id = fields.Many2one(
        comodel_name="product.template", string="Nested product template"
    )
