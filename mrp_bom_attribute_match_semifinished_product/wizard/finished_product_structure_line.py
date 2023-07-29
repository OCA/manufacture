from odoo import _, api, fields, models


class FinishedProductStructureLine(models.TransientModel):
    _name = "finished.product.structure.line"

    structure_id = fields.Many2one("finished.product.structure.wizard")
    stage_name = fields.Char(required=True)
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        required=True,
        string="Template product",
    )
    valid_attribute_ids = fields.Many2many(
        comodel_name="product.attribute",
        relation="product_attribute_valid_rel",
    )
    attribute_ids = fields.Many2many(
        comodel_name="product.attribute",
        relation="finished_product_struct_line_attribute_rel",
        domain="[('id', 'in', valid_attribute_ids)]",
        required=True,
        string="Attribute(s)",
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
    partner_ids = fields.Many2many(comodel_name="res.partner", string="Subcontractor")
    product_tmpl_stage_id = fields.Many2one(comodel_name="product.template")

    @api.onchange("product_tmpl_id")
    def _onchange_product_tmpl_id(self):
        self._check_product_tmpl_id()

    @api.constrains("product_tmpl_id")
    def _check_product_tmpl_id(self):
        for rec in self:
            if rec.product_tmpl_id.attribute_line_ids:
                raise models.ValidationError(
                    _(
                        "You can only add products without attributes as 'Template products'."
                    )
                )

    @api.model
    def default_get(self, fields):
        result = super(FinishedProductStructureLine, self).default_get(fields)
        if result.get("valid_attribute_ids"):
            result["attribute_ids"] = result["valid_attribute_ids"]
        return result
