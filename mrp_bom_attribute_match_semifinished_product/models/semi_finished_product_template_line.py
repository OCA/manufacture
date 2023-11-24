from odoo import fields, models


class SemiFinishedProductTemplateLine(models.Model):
    _name = "semi.finished.product.template.line"

    product_tmpl_id = fields.Many2one(comodel_name="product.template")
    semi_finished_product_tmpl_id = fields.Many2one(
        comodel_name="product.template", string="Semi-finished Product"
    )
    attribute_ids = fields.Many2many(
        comodel_name="product.attribute",
        relation="semi_finished_product_template_line_rel",
    )
    bom_type = fields.Selection(
        selection=[
            ("normal", "Manufacture this product"),
            ("phantom", "Kit"),
            ("subcontract", "Subcontracting"),
        ],
        default="normal",
        required=True,
    )
    partner_ids = fields.Many2many(comodel_name="res.partner", string="Subcontractors")
