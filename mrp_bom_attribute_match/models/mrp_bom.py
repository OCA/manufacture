import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round

_log = logging.getLogger(__name__)


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    product_id = fields.Many2one("product.product", "Component", required=False)
    product_backup_id = fields.Many2one(
        "product.product", help="Technical field to store previous value of product_id"
    )
    component_template_id = fields.Many2one(
        "product.template", "Component (product template)"
    )
    match_on_attribute_ids = fields.Many2many(
        "product.attribute",
        string="Match on Attributes",
        compute="_compute_match_on_attribute_ids",
        store=True,
    )
    product_uom_category_id = fields.Many2one(
        "uom.category",
        related=None,
        compute="_compute_product_uom_category_id",
    )

    @api.onchange("component_template_id")
    def _onchange_component_template_id(self):
        product_id = self.product_id
        component_template_id = self.component_template_id

        if component_template_id:
            if product_id:
                self.product_backup_id = product_id
                self.product_id = False

            if (
                self.product_uom_id.category_id
                != component_template_id.uom_id.category_id
            ):
                self.product_uom_id = component_template_id.uom_id

        else:
            product_uom_id = product_id.uom_id

            if self.product_backup_id:
                self.product_id = self.product_backup_id
                self.product_backup_id = False

            if self.product_uom_id.category_id != product_uom_id.category_id:
                self.product_uom_id = product_uom_id

    @api.onchange("bom_product_template_attribute_value_ids")
    def _onchange_bom_product_template_attribute_value_ids_check_variants(self):
        if self.bom_product_template_attribute_value_ids:
            self._check_variants_validity()

    @api.depends("component_template_id")
    def _compute_match_on_attribute_ids(self):
        for line_id in self:
            component_template_id = line_id.component_template_id

            if component_template_id:
                line_id.match_on_attribute_ids = (
                    component_template_id.attribute_line_ids.attribute_id._without_no_variant_attributes()
                )

            else:
                line_id.match_on_attribute_ids = False

    @api.depends("product_id", "component_template_id")
    def _compute_product_uom_category_id(self):
        """Compute the product_uom_category_id field.

        This is the product category that will be allowed to use on the product_uom_id
        field, already covered by core module:
        https://github.com/odoo/odoo/blob/331b9435c/addons/mrp/models/mrp_bom.py#L372

        In core, though, this field is related to "product_id.uom_id.category_id".
        Here we make it computed to choose between component_template_id and
        product_id, depending on which one is set
        """
        # NOTE: To play nice with other modules trying to do the same:
        #   1) Set the field value as if it were a related field (core behaviour)
        #   2) Call super (if it's there)
        #   3) Update only the records we want
        for line_id in self:
            line_id.product_uom_category_id = line_id.product_id.uom_id.category_id

            if line_id.component_template_id:
                line_id.product_uom_category_id = (
                    line_id.component_template_id.uom_id.category_id
                )

    @api.constrains("component_template_id")
    def _check_component_attributes(self):
        for line_id in self.filtered("component_template_id"):
            component_template_id = line_id.component_template_id
            component_attribute_ids = (
                component_template_id.valid_product_template_attribute_line_ids.attribute_id
            )

            if not component_attribute_ids:
                raise ValidationError(
                    _(
                        "No match on attribute has been detected for Component (Product Template) %s",
                        component_template_id.display_name,
                    )
                )

            if not set(component_attribute_ids.ids).issubset(
                line_id.bom_id.product_tmpl_id.valid_product_template_attribute_line_ids.attribute_id.ids
            ):
                raise ValidationError(
                    _(
                        "Some attributes of the dynamic component are not included into production product attributes."
                    )
                )

    @api.constrains("component_template_id", "bom_product_template_attribute_value_ids")
    def _check_variants_validity(self):
        for line_id in self.filtered(
            lambda l_id: l_id.bom_product_template_attribute_value_ids
            and l_id.component_template_id
        ):
            same_attribute_ids = (
                line_id.match_on_attribute_ids
                & line_id.bom_product_template_attribute_value_ids.attribute_id
            )

            if same_attribute_ids.exists():
                raise ValidationError(
                    _(
                        "You cannot use an attribute value for attribute(s) "
                        "%(same_attribute_names)s in the field “Apply on Variants” as it's the "
                        "same attribute used in the field “Match on Attribute” related "
                        "to the component %(component_name)s.",
                        same_attribute_names=", ".join(
                            same_attribute_ids.mapped("name")
                        ),
                        component_name=line_id.component_template_id.name,
                    )
                )


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _get_component_or_product_id(
        self, bom_line_id, bom_product_id, line_product_id
    ):
        component_template_id = bom_line_id.component_template_id

        if not component_template_id:
            return line_product_id

        # check attributes
        if not {
            component_template_id.valid_product_template_attribute_line_ids.attribute_id
        }.issubset(
            bom_product_id.valid_product_template_attribute_line_ids.attribute_id
        ):
            _log.info(
                "Component skipped. Component attributes must be included into "
                "product attributes to use component_template_id."
            )

            return

        # find matching combination
        combination_ids = self.env["product.template.attribute.value"]

        for bom_product_ptav_id in bom_product_id.product_template_attribute_value_ids:
            combination_ids |= self.env["product.template.attribute.value"].search(
                [
                    ("product_tmpl_id", "=", component_template_id.id),
                    ("attribute_id", "=", bom_product_ptav_id.attribute_id.id),
                    (
                        "product_attribute_value_id",
                        "=",
                        bom_product_ptav_id.product_attribute_value_id.id,
                    ),
                ]
            )

        if not combination_ids:
            return

        product_id = component_template_id._get_variant_for_combination(
            combination_ids
        ) or component_template_id._create_product_variant(combination_ids)

        return product_id.active and product_id

    def explode(self, product, quantity, picking_type=False):
        """
        Explodes the BoM and creates two lists with all the information you need:
        bom_done and line_done
        Quantity describes the number of times you need the BoM: so the quantity
        divided by the number created by the BoM
        and converted into its UoM
        """
        from collections import defaultdict

        dependency_graph = defaultdict(list)
        processed_templates = set()

        def check_cycle(current_node, visited_nodes, recursion_stack, dependency_graph):
            visited_nodes[current_node] = True
            recursion_stack[current_node] = True

            for neighbour in dependency_graph[current_node]:
                if visited_nodes[neighbour] is False:
                    if (
                        check_cycle(
                            neighbour, visited_nodes, recursion_stack, dependency_graph
                        )
                        is True
                    ):
                        return True

                elif recursion_stack[neighbour] is True:
                    return True

            recursion_stack[current_node] = False

            return False

        products = set()
        product_boms = {}

        def update_product_boms():
            product_ids = self.env["product.product"].browse(products)

            product_boms.update(
                self._bom_find(
                    product_ids,
                    bom_type="phantom",
                    picking_type=picking_type or self.picking_type_id,
                    company_id=self.company_id.id,
                )
            )

            # Set missing keys to default value
            for product_id in product_ids:
                product_boms.setdefault(product_id, self.env["mrp.bom"])

        boms_done = [
            (
                self,
                {
                    "qty": quantity,
                    "product": product,
                    "original_qty": quantity,
                    "parent_line": False,
                },
            )
        ]

        lines_done = []
        processed_templates |= {product.product_tmpl_id.id}
        bom_lines = []

        for bom_line_id in self.bom_line_ids:
            product_id = bom_line_id.product_id
            processed_templates |= {product_id.product_tmpl_id.id}
            dependency_graph[product.product_tmpl_id.id].append(
                product_id.product_tmpl_id.id
            )
            bom_lines.append((bom_line_id, product, quantity, False))
            products.add(product_id.id)

        update_product_boms()
        products.clear()

        while bom_lines:
            (
                current_line_id,
                current_product_id,
                current_qty,
                parent_line_id,
            ) = bom_lines[0]
            bom_lines = bom_lines[1:]

            if current_line_id._skip_bom_line(current_product_id):
                continue

            line_quantity = current_qty * current_line_id.product_qty

            if current_line_id.product_id not in product_boms:
                update_product_boms()
                products.clear()

            # upd start
            component_template_product_id = self._get_component_or_product_id(
                current_line_id, product, current_line_id.product_id
            )

            if component_template_product_id:
                # need to set product_id temporary
                current_line_id.product_id = component_template_product_id

            else:
                # component_template_id is set, but no attribute value match.
                continue
            # upd end

            bom_id = product_boms.get(current_line_id.product_id)

            if bom_id:
                converted_line_quantity = (
                    current_line_id.product_uom_id._compute_quantity(
                        line_quantity / bom_id.product_qty, bom_id.product_uom_id
                    )
                )

                bom_lines.extend(
                    (
                        line_id,
                        current_line_id.product_id,
                        converted_line_quantity,
                        current_line_id,
                    )
                    for line_id in bom_id.bom_line_ids
                )

                for bom_line_id in bom_id.bom_line_ids:
                    dependency_graph[
                        current_line_id.product_id.product_tmpl_id.id
                    ].append(bom_line_id.product_id.product_tmpl_id.id)

                    if (
                        bom_line_id.product_id.product_tmpl_id.id in processed_templates
                        and check_cycle(
                            bom_line_id.product_id.product_tmpl_id.id,
                            {key: False for key in processed_templates},
                            {key: False for key in processed_templates},
                            dependency_graph,
                        )
                    ):
                        raise UserError(
                            _(
                                "Recursion error!  A product with a Bill of Material "
                                "should not have itself in its BoM or child BoMs!"
                            )
                        )

                    processed_templates |= {bom_line_id.product_id.product_tmpl_id.id}

                    if bom_line_id.product_id not in product_boms:
                        products.add(bom_line_id.product_id.id)

                boms_done.append(
                    (
                        bom_id,
                        {
                            "qty": converted_line_quantity,
                            "product": current_product_id,
                            "original_qty": quantity,
                            "parent_line": current_line_id,
                        },
                    )
                )

            else:
                # We round up here because the user expects
                # that if he has to consume a little more, the whole UOM unit
                # should be consumed.
                line_quantity = float_round(
                    line_quantity,
                    precision_rounding=current_line_id.product_uom_id.rounding,
                    rounding_method="UP",
                )

                lines_done.append(
                    (
                        current_line_id,
                        {
                            "qty": line_quantity,
                            "product": current_product_id,
                            "original_qty": quantity,
                            "parent_line": parent_line_id,
                        },
                    )
                )

        return boms_done, lines_done

    @api.constrains("product_tmpl_id", "product_id")
    def _check_component_attributes(self):
        self.bom_line_ids._check_component_attributes()

    @api.constrains("product_tmpl_id", "product_id")
    def _check_variants_validity(self):
        self.bom_line_ids._check_variants_validity()
