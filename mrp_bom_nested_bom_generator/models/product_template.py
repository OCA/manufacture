from odoo import _, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    nested_bom_ids = fields.One2many(
        comodel_name="mrp.nested.bom",
        inverse_name="parent_id",
    )
    nested_bom_count = fields.Integer(
        compute="_compute_nested_bom_count",
        string="Nested Bom Count",
    )
    changed_nested_bom = fields.Boolean(string="Changed Nested Bom", default=True)

    def _compute_nested_bom_count(self) -> None:
        """
        Compute count nested BOM lines
        :return None
        """
        for rec in self:
            rec.nested_bom_count = len(rec.nested_bom_ids)

    def _prepare_temp_nested_bom_item(self) -> models.Model:
        """
        Prepare temp nested bom for current product template
        :return temp nested bom record
        :rtype mrp.nested.bom()
        """
        return self.nested_bom_ids.new(
            {
                "parent_id": self.id,
                "product_tmpl_id": self.id,
                "product_qty": 1,
                "uom_id": self.uom_id.id,
            }
        )

    def group_by_stage(self) -> list:
        """
        Group nested bom line by stage
        :yield list(MRP product, component)
        :
        """
        nestings = [
            self._prepare_temp_nested_bom_item(),
        ] + list(self.nested_bom_ids.sorted(lambda line: line.sequence))
        for i in range(1, len(nestings)):
            yield nestings[i - 1], nestings[i]

    def unlink_existing_bom(self) -> bool:
        """
        Unlink BOM by product.template
        :return: bool
        """
        mrp_bom_ids = self.env["mrp.bom"].search(
            [("nested_product_template_id", "=", self.id)]
        )
        if not len(mrp_bom_ids) > 0:
            return False
        used_mrp_bom_ids = (
            self.env["mrp.production"]
            .search([("bom_id", "in", mrp_bom_ids.ids)])
            .mapped("bom_id")
        )
        unused_mrp_bom_ids = mrp_bom_ids.filtered(
            lambda bom: bom.id not in used_mrp_bom_ids.ids
        )
        used_mrp_bom_ids.sudo().write({"active": False})
        unused_mrp_bom_ids.sudo().unlink()
        return True

    def create_boms(self) -> None:
        """
        Create BOM for stage
        :return None
        """
        self.unlink_existing_bom()
        for product, component in self.group_by_stage():
            bom_lines = component._prepare_bom_lines(product)
            line_ptavs = [
                line[2]["bom_product_template_attribute_value_ids"]
                for line in bom_lines
            ]
            if all(line_ptavs) or len(bom_lines) == 1:
                self.env["mrp.bom"].create(
                    {
                        "product_tmpl_id": product.product_tmpl_id.id,
                        "product_uom_id": product.uom_id.id,
                        "product_qty": product.product_qty,
                        "type": "normal",
                        "bom_line_ids": bom_lines,
                        "nested_product_template_id": self.id,
                    }
                )
            else:
                for line in bom_lines:
                    self.env["mrp.bom"].create(
                        {
                            "product_tmpl_id": product.product_tmpl_id.id,
                            "product_uom_id": product.uom_id.id,
                            "product_qty": product.product_qty,
                            "type": "normal",
                            "bom_line_ids": [
                                line,
                            ],
                            "nested_product_template_id": self.id,
                        }
                    )

    def action_generate_nested_boms(self) -> bool:
        """
        Generate MRP BOM by nested BOM
        :raise UserError Nested BOM is Empty
        :return bool
        """
        self.ensure_one()
        if not self.nested_bom_count > 0:
            raise models.UserError(_("Nested BOM is Empty!"))
        if not self.changed_nested_bom:
            return False
        self.nested_bom_ids._prepare_product_attribute()
        self.create_boms()
        self.changed_nested_bom = False
        return True
