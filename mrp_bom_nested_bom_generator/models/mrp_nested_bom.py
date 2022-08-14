from typing import Any, Dict, Set

from odoo import _, api, fields, models


class MrpNestedBomLine(models.Model):
    _name = "mrp.nested.bom"
    _description = "MRP Nested BOM Line"

    sequence = fields.Integer(string="Sequence", default=10)

    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="MRP BOM",
        required=True,
    )

    bom_product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Template",
        related="bom_id.product_tmpl_id",
    )

    attribute_aggregated_ids = fields.Many2many(
        "product.attribute",
        "attribute_aggregated_ids_ref",
        string="Parent Product Template attribute",
        compute="_compute_attribute_aggregated_ids",
        store=True,
    )

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product",
        domain="[('id', '!=', bom_product_tmpl_id)]",
    )
    product_qty = fields.Float(
        string="Qty",
        default=1,
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

    @api.depends("bom_id.nested_bom_ids", "bom_product_tmpl_id.attribute_line_ids")
    def _compute_attribute_aggregated_ids(self) -> None:
        """
        Compute product attributes by parent product and component
        :return None
        """
        for rec in self:
            default_attributes = rec.product_tmpl_id.attribute_line_ids.mapped(
                "attribute_id"
            )
            parent_attributes = rec.bom_product_tmpl_id.attribute_line_ids.mapped(
                "attribute_id"
            )
            attributes_ids = default_attributes | parent_attributes
            rec.attribute_aggregated_ids = attributes_ids

    @api.model
    def create_product(self, bom) -> int:
        """
        Create product by parent product
        :param bom: mrp.bom record
        :return new product template id
        :rtype int or bool
        """
        if not bom:
            return False
        nested_bom_count: int = self.search_count(
            [("bom_product_tmpl_id", "=", bom.product_tmpl_id.id)]
        )
        return (
            self.env["product.template"]
            .create(
                {
                    "name": "{} #{}".format(
                        bom.product_tmpl_id.name, nested_bom_count + 1
                    )
                }
            )
            .id
        )

    @api.model
    def create(self, vals: Dict[str, Any]):
        product_tmpl_id = vals.get("product_tmpl_id", False)
        product_qty = vals.get("product_qty", False)
        bom_id = vals.get("bom_id", False)
        bom = self.env["mrp.bom"].browse(bom_id)
        # Create product template if product_tmpl_id not set
        if not product_tmpl_id:
            pt_id = self.create_product(bom)
            if pt_id:
                vals.update(product_tmpl_id=self.create_product(bom))

        # Raising Exception if product qty less or equal zero
        if product_qty <= 0.0:
            raise models.ValidationError(_("Nested BOM: Product Qty must be than 0.0"))
        return super(MrpNestedBomLine, self).create(vals)

    def _prepare_parent_attribute_ids(self) -> Set[int]:
        """
        Get parent product template attribute ids
        :return set attributes ids Any
        :rtype set()
        """
        self.ensure_one()
        component_attributes_set_ids = set(self.attribute_ids.ids)
        parent_attributes_ids = self.bom_product_tmpl_id.attribute_line_ids.mapped(
            "attribute_id"
        ).ids
        return component_attributes_set_ids.intersection(parent_attributes_ids)

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
        for rec in self:
            attr_ids = rec._prepare_parent_attribute_ids()
            if not len(attr_ids) > 0:
                continue
            product_attr_ids = rec._find_product_template_attributes(attr_ids)
            sub_ids = set(attr_ids) - set(product_attr_ids.ids)
            if len(sub_ids) > 0:
                pta_line_ids = rec.bom_product_tmpl_id.attribute_line_ids.filtered(
                    lambda l: l.attribute_id.id in sub_ids
                )
                for line in pta_line_ids:
                    line.copy(default={"product_tmpl_id": rec.product_tmpl_id.id})

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
        product_attribute_value = (
            main_line.product_tmpl_id.attribute_line_ids.product_template_value_ids
        )
        for variant in product_variant_ids:
            attr_values_ids = variant.product_template_attribute_value_ids.mapped(
                "product_attribute_value_id.id"
            )
            filter_ptav_main = product_attribute_value.filtered(
                lambda v: v.product_attribute_value_id.id in attr_values_ids
            )
            vals = {
                "product_id": variant.id,
                "product_qty": self.product_qty,
                "bom_product_template_attribute_value_ids": [
                    (4, pid) for pid in filter_ptav_main.ids
                ],
            }
            bom_line_vals.append((0, 0, vals))
        return bom_line_vals
