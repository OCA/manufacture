from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    finished_product = fields.Boolean()
    semi_finished_product_tmpl_ids = fields.One2many(
        comodel_name="semi.finished.product.template.line",
        inverse_name="product_tmpl_id",
        groups="mrp.group_mrp_user",
    )
    semi_finished_mrp_bom_ids = fields.Many2many(
        comodel_name="mrp.bom", string="MRP BoM"
    )

    @api.constrains("finished_product", "attribute_line_ids")
    def _check_finished_product(self):
        for rec in self.filtered("finished_product"):
            if not rec.attribute_line_ids:
                raise models.UserError(
                    _(
                        "Finished product is meant to be used only "
                        "on products with attributes in order "
                        "to create a BOM structure for its semi-finished "
                        "products based on attribute value match"
                    )
                )

    def action_finished_product_structure(self):
        self.ensure_one()
        if not self.finished_product:
            raise models.UserError(
                _(
                    "You can only create finished product structure "
                    'for products marked as "Finished product".'
                )
            )
        return {
            "name": _("Create finished product structure"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "finished.product.structure.wizard",
            "context": {
                "default_finished_product_id": self.id,
            },
            "target": "new",
        }
