from typing import Any, Dict

from odoo import _, api, fields, models


class MrpNestedBomLine(models.Model):
    _name = "mrp.nested.bom"
    _description = "MRP Nested BOM Line"

    sequence = fields.Integer(string="Sequence", default=10)

    parent_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Template",
        required=True,
    )

    all_attribute_ids = fields.Many2many(
        "product.attribute",
        "all_attribute_ids_ref",
        string="Parent Product Template attribute",
        compute="_compute_all_attribute_ids",
        store=True,
    )

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product",
        domain="[('id', '!=', parent_id)]",
    )
    product_qty = fields.Float(
        string="Qty",
        required=True,
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        related="product_tmpl_id.uom_id",
        readonly=True,
    )

    attribute_ids = fields.Many2many(
        "product.attribute",
        "attribute_ids_ref",
        string="Attributes",
    )

    @api.onchange("product_tmpl_id")
    def _onchange_product_tmpl_id(self) -> None:
        """
        Change attribute field at changing product template field
        :return None
        """
        self.attribute_ids = self.product_tmpl_id.attribute_line_ids.mapped(
            "attribute_id"
        )

    @api.depends("parent_id.nested_bom_ids", "parent_id.attribute_line_ids")
    def _compute_all_attribute_ids(self) -> None:
        """
        Compute product attributes by parent product and component
        :return None
        """
        for rec in self:
            default_attributes = rec.product_tmpl_id.attribute_line_ids.mapped(
                "attribute_id"
            )
            parent_attributes = rec.parent_id.attribute_line_ids.mapped("attribute_id")
            attributes_ids = default_attributes | parent_attributes
            rec.all_attribute_ids = attributes_ids

    @api.model
    def create_product(self, parent_product_id: int) -> int:
        """
        Create product by parent product
        :param int parent_product_id: product.template record id
        :return new product template id
        :rtype int
        """
        product_template = self.env["product.template"].browse(parent_product_id)
        nested_bom_count: int = self.search_count(
            [("parent_id", "=", parent_product_id)]
        )
        return (
            self.env["product.template"]
            .create(
                {"name": "{} #{}".format(product_template.name, nested_bom_count + 1)}
            )
            .id
        )

    @api.model
    def create(self, vals: Dict[str, Any]):
        parent_id = vals.get("parent_id", False)
        product_tmpl_id = vals.get("product_tmpl_id", False)
        product_qty = vals.get("product_qty", False)

        # Create product template if product_tmpl_id not set
        if not product_tmpl_id:
            vals.update(product_tmpl_id=self.create_product(parent_id))

        # Raising Exception if product qty less or equal zero
        if product_qty <= 0.0:
            raise models.ValidationError(_("Nested BOM: Product Qty must be than 0.0"))
        return super(MrpNestedBomLine, self).create(vals)

    def _prepare_parent_attribute_ids(self) -> None:
        """
        Get parent product template attribute ids
        :return recordset
        :rtype product.attribute()
        """
        self.ensure_one()
        return self.parent_id.attribute_line_ids.mapped("attribute_id").ids

    def _find_product_template_attributes(self, attr_ids) -> models.Model:
        """
        Get attribute ids included in attr_ids
        :param list attr_ids: list of attribute ids
        :return recordset
        :rtype product.attribute()
        """
        return self.product_tmpl_id.attribute_line_ids.mapped("attribute_id").filtered(
            lambda attr_: attr_.id in attr_ids
        )

    def _prepare_product_attribute(self) -> None:
        """
        Add missing attributes to the mrp product by component
        :return None
        """
        for index in range(1, len(self)):
            main_product, component = self[index - 1], self[index]
            attrs_ids = component._prepare_parent_attribute_ids()
            if not len(attrs_ids) > 0:
                continue
            has_attribute = main_product._find_product_template_attributes(attrs_ids)
            sub_ids = set(attrs_ids) - set(has_attribute.ids)
            if len(sub_ids) == 0:
                continue
            pta_line_ids = main_product.parent_id.attribute_line_ids.filtered(
                lambda l: l.attribute_id.id in sub_ids
            )
            for line in pta_line_ids:
                line.copy(default={"product_tmpl_id": main_product.product_tmpl_id.id})

    def _prepare_bom_lines(self, main_line: models.Model) -> list:
        """
        Prepare MRP BOM lines for Nested BOM line
        :param main_line: mrp.nested.bom record
        :return list BOM lines
        :rtype list
        """
        self.ensure_one()
        bom_line_vals = []
        product_variant_ids = self.product_tmpl_id.product_variant_ids
        for variant in product_variant_ids:
            attr_values_ids = variant.product_template_attribute_value_ids.mapped(
                "product_attribute_value_id.id"
            )
            ptav = (
                main_line.product_tmpl_id.attribute_line_ids.product_template_value_ids
            )
            filter_ptav_main = ptav.filtered(
                lambda v: v.product_attribute_value_id.id in attr_values_ids
            )
            bom_line_vals.append(
                (
                    0,
                    0,
                    {
                        "product_id": variant.id,
                        "product_qty": self.product_qty,
                        "bom_product_template_attribute_value_ids": [
                            (4, pid) for pid in filter_ptav_main.ids
                        ],
                    },
                )
            )
        return bom_line_vals
