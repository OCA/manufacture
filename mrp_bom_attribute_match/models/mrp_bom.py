import logging
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    product_id = fields.Many2one("product.product", "Component", required=False)
    product_backup_id = fields.Many2one(
        "product.product",
        help="Technical field to store previous value of product_id",
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

    @api.model_create_multi
    def create(self, vals_list):
        """Inherit so that, when a bom line is created with only a
        ``component_template_id`` and no explicit UoM, we pick the template's
        UoM. Core mrp marks ``product_uom_id`` as required and its default
        derives from ``product_id``, which is empty in this case.
        """
        for values in vals_list:
            if (
                not values.get("product_id")
                and not values.get("product_uom_id")
                and values.get("component_template_id")
            ):
                template = self.env["product.template"].browse(
                    values["component_template_id"]
                )
                values["product_uom_id"] = template.uom_id.id
        return super().create(vals_list)

    @api.onchange("component_template_id")
    def _onchange_component_template_id(self):
        component = self.component_template_id
        if component:
            if self.product_id:
                self.product_backup_id = self.product_id
                self.product_id = False
            if self.product_uom_id.category_id != component.uom_id.category_id:
                self.product_uom_id = component.uom_id
        else:
            if self.product_backup_id:
                self.product_id = self.product_backup_id
                self.product_backup_id = False
            if (
                self.product_id
                and self.product_uom_id.category_id != self.product_id.uom_id.category_id
            ):
                self.product_uom_id = self.product_id.uom_id

    @api.onchange("bom_product_template_attribute_value_ids")
    def _onchange_bom_product_template_attribute_value_ids_check_variants(self):
        if self.bom_product_template_attribute_value_ids:
            self._check_variants_validity()

    @api.depends("component_template_id")
    def _compute_match_on_attribute_ids(self):
        for line in self:
            if line.component_template_id:
                line.match_on_attribute_ids = (
                    line.component_template_id.attribute_line_ids.attribute_id
                    ._without_no_variant_attributes()
                )
            else:
                line.match_on_attribute_ids = False

    @api.depends("product_id", "component_template_id")
    def _compute_product_uom_category_id(self):
        """Resolve the UoM category from either the component template or
        the product, depending on which one is set."""
        for line in self:
            line.product_uom_category_id = line.product_id.uom_id.category_id
            if line.component_template_id:
                line.product_uom_category_id = (
                    line.component_template_id.uom_id.category_id
                )

    @api.constrains("component_template_id")
    def _check_component_attributes(self):
        for line in self.filtered("component_template_id"):
            component = line.component_template_id
            component_attrs = (
                component.valid_product_template_attribute_line_ids.attribute_id
            )
            product_attrs = (
                line.bom_id.product_tmpl_id
                .valid_product_template_attribute_line_ids.attribute_id
            )
            if not component_attrs:
                raise ValidationError(
                    _(
                        "No match on attribute has been detected for Component "
                        "(Product Template) %s",
                        component.display_name,
                    )
                )
            # NOTE: `<=`/`<` on Odoo recordsets compares the `_ids` tuples
            # lexicographically, which is NOT a subset check. Use explicit
            # `in` membership (which is well-defined by record id) instead.
            if not all(attr in product_attrs for attr in component_attrs):
                raise ValidationError(
                    _(
                        "Some attributes of the dynamic component are not included "
                        "into production product attributes."
                    )
                )

    @api.constrains("component_template_id", "bom_product_template_attribute_value_ids")
    def _check_variants_validity(self):
        for line in self.filtered(
            lambda l: l.bom_product_template_attribute_value_ids
            and l.component_template_id
        ):
            overlap = (
                line.match_on_attribute_ids
                & line.bom_product_template_attribute_value_ids.attribute_id
            )
            if overlap:
                raise ValidationError(
                    _(
                        "You cannot use an attribute value for attribute(s) "
                        "%(attributes)s in the field “Apply on Variants” as it's the "
                        "same attribute used in the field “Match on Attribute” "
                        "related to the component %(component)s.",
                        attributes=", ".join(overlap.mapped("name")),
                        component=line.component_template_id.name,
                    )
                )


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _get_component_or_product_id(self, bom_line, bom_product, line_product):
        """Resolve which product to use for a BoM line.

        If the line uses a dynamic component template, find the matching variant
        based on the parent product's attribute values. Returns an empty recordset
        when no variant matches (the line is then skipped by `explode`).
        """
        component = bom_line.component_template_id
        if not component:
            return line_product

        # Component attributes must be a subset of the parent product's.
        # NOTE: do not use `<=` between recordsets — see `_check_component_attributes`.
        component_attrs = component.valid_product_template_attribute_line_ids.attribute_id
        product_attrs = bom_product.valid_product_template_attribute_line_ids.attribute_id
        if not all(attr in product_attrs for attr in component_attrs):
            _logger.info(
                "Component skipped: component template '%s' attributes are not "
                "included in product '%s' attributes.",
                component.display_name,
                bom_product.display_name,
            )
            return self.env["product.product"]

        # Find the matching attribute combination on the component template.
        combination = self.env["product.template.attribute.value"]
        for ptav in bom_product.product_template_attribute_value_ids:
            combination |= self.env["product.template.attribute.value"].search(
                [
                    ("product_tmpl_id", "=", component.id),
                    ("attribute_id", "=", ptav.attribute_id.id),
                    ("product_attribute_value_id", "=", ptav.product_attribute_value_id.id),
                ]
            )
        if not combination:
            return self.env["product.product"]

        variant = component._get_variant_for_combination(
            combination
        ) or component._create_product_variant(combination)
        if variant and variant.active:
            return variant
        return self.env["product.product"]

    def _has_dynamic_components(self):
        """True if any bom line resolves through a component template."""
        return any(line.component_template_id for line in self.bom_line_ids)

    def explode(self, product, quantity, picking_type=False):
        """Explode the BoM into ``(boms_done, lines_done)``.

        Quantity describes how many times the BoM has to be run.

        This override keeps the original API but resolves dynamic component
        templates against the parent product's variant. To avoid persisting the
        resolved variant on the live ``mrp.bom.line`` record (which would race
        between concurrent callers and leave the BoM in a dirty state on
        rollback), the explosion runs against an in-memory copy of the BoM
        whenever any line uses a component template. The same pattern is used
        in ``reports/mrp_report_bom_structure.py``.
        """
        # Virtualise the root BoM if needed. ``self.new(origin=self)`` returns
        # a record whose ``_origin`` points back to the persisted one, so all
        # computed fields keep working but writes stay in memory.
        if self._has_dynamic_components():
            self = self.new(origin=self)

        dependency_graph = defaultdict(list)
        visited_templates = set()

        def has_cycle(node, visited, stack):
            visited[node] = True
            stack[node] = True
            for neighbour in dependency_graph[node]:
                if not visited.get(neighbour) and has_cycle(neighbour, visited, stack):
                    return True
                if stack.get(neighbour):
                    return True
            stack[node] = False
            return False

        pending_product_ids = set()
        product_boms = {}

        def refresh_product_boms():
            products = self.env["product.product"].browse(pending_product_ids)
            product_boms.update(
                self._bom_find(
                    products,
                    bom_type="phantom",
                    picking_type=picking_type or self.picking_type_id,
                    company_id=self.company_id.id,
                )
            )
            for prod in products:
                product_boms.setdefault(prod, self.env["mrp.bom"])

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
        visited_templates.add(product.product_tmpl_id.id)

        bom_lines = []
        for bom_line in self.bom_line_ids:
            line_product = bom_line.product_id
            if line_product:
                visited_templates.add(line_product.product_tmpl_id.id)
                dependency_graph[product.product_tmpl_id.id].append(
                    line_product.product_tmpl_id.id
                )
                pending_product_ids.add(line_product.id)
            bom_lines.append((bom_line, product, quantity, False))

        refresh_product_boms()
        pending_product_ids.clear()

        while bom_lines:
            current_line, current_product, current_qty, parent_line = bom_lines.pop(0)

            if current_line._skip_bom_line(current_product):
                continue

            # Resolve the dynamic component FIRST so the BoM lookup that
            # follows sees the resolved variant.
            resolved_product = self._get_component_or_product_id(
                current_line, current_product, current_line.product_id
            )
            if not resolved_product:
                # Dynamic component with no matching variant: skip the line.
                continue

            # Safe in-memory write: `current_line` is virtual whenever its
            # parent BoM was virtualised at the top of this method, or below
            # before child lines were queued.
            if current_line.product_id != resolved_product:
                current_line.product_id = resolved_product

            line_quantity = current_qty * current_line.product_qty

            if current_line.product_id not in product_boms:
                pending_product_ids.add(current_line.product_id.id)
                refresh_product_boms()
                pending_product_ids.clear()

            child_bom = product_boms.get(current_line.product_id)
            if child_bom:
                # Virtualise the child BoM too if it has dynamic components,
                # so we never persist resolved variants on its lines either.
                if child_bom._has_dynamic_components():
                    child_bom = child_bom.new(origin=child_bom)

                converted_line_quantity = current_line.product_uom_id._compute_quantity(
                    line_quantity / child_bom.product_qty, child_bom.product_uom_id
                )
                bom_lines.extend(
                    (line, current_line.product_id, converted_line_quantity, current_line)
                    for line in child_bom.bom_line_ids
                )

                for line in child_bom.bom_line_ids:
                    dependency_graph[
                        current_line.product_id.product_tmpl_id.id
                    ].append(line.product_id.product_tmpl_id.id)
                    if line.product_id.product_tmpl_id.id in visited_templates:
                        if has_cycle(
                            line.product_id.product_tmpl_id.id,
                            {key: False for key in visited_templates},
                            {key: False for key in visited_templates},
                        ):
                            raise UserError(
                                _(
                                    "Recursion error! A product with a Bill of "
                                    "Material should not have itself in its BoM "
                                    "or child BoMs!"
                                )
                            )
                    visited_templates.add(line.product_id.product_tmpl_id.id)
                    if line.product_id not in product_boms:
                        pending_product_ids.add(line.product_id.id)

                boms_done.append(
                    (
                        child_bom,
                        {
                            "qty": converted_line_quantity,
                            "product": current_product,
                            "original_qty": quantity,
                            "parent_line": current_line,
                        },
                    )
                )
            else:
                line_quantity = float_round(
                    line_quantity,
                    precision_rounding=current_line.product_uom_id.rounding,
                    rounding_method="UP",
                )
                lines_done.append(
                    (
                        current_line,
                        {
                            "qty": line_quantity,
                            "product": current_product,
                            "original_qty": quantity,
                            "parent_line": parent_line,
                        },
                    )
                )

        return boms_done, lines_done

    @api.constrains("product_tmpl_id", "bom_line_ids")
    def _check_component_attributes(self):
        self.bom_line_ids._check_component_attributes()

    @api.constrains("product_tmpl_id", "bom_line_ids")
    def _check_variants_validity(self):
        self.bom_line_ids._check_variants_validity()
