import json
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
        "product.attribute", string="Match on Attributes", readonly=True
    )
    product_uom_id_domain = fields.Char(compute="_compute_product_uom_id_domain")

    @api.depends("component_template_id", "product_id")
    def _compute_product_uom_id_domain(self):
        for r in self:
            if r.component_template_id:
                category_id = r.component_template_id.uom_id.category_id.id
                if (
                    r.product_uom_id.category_id.id
                    != r.component_template_id.uom_id.category_id.id
                ):
                    r.product_uom_id = r.component_template_id.uom_id
            else:
                category_id = r.product_uom_category_id.id
            r.product_uom_id_domain = json.dumps([("category_id", "=", category_id)])

    @api.onchange("component_template_id")
    def _onchange_component_template_id(self):
        self.update_component_attributes()

    def update_component_attributes(self):
        if self.component_template_id:
            self.check_component_attributes()
            self.product_backup_id = self.product_id.id
            self.match_on_attribute_ids = (
                self.component_template_id.attribute_line_ids.mapped("attribute_id")
                .filtered(lambda x: x.create_variant != "no_variant")
                .ids
            )
            self.product_id = False
            self.check_variants_validity()
        else:
            self.match_on_attribute_ids = False
            if self.product_backup_id and not self.product_id:
                self.product_id = self.product_backup_id.id
                self.product_backup_id = False

    def check_component_attributes(self):
        comp_attr_ids = (
            self.component_template_id.valid_product_template_attribute_line_ids.attribute_id.ids
        )
        prod_attr_ids = (
            self.bom_id.product_tmpl_id.valid_product_template_attribute_line_ids.attribute_id.ids
        )
        if len(comp_attr_ids) == 0:
            raise ValidationError(
                _(
                    "No match on attribute has been detected for Component "
                    "(Product Template) %s" % self.component_template_id.display_name
                )
            )
        if not all(item in prod_attr_ids for item in comp_attr_ids):
            raise ValidationError(
                _(
                    "Some attributes of the dynamic component are not included into "
                    "production product attributes."
                )
            )

    @api.onchange("bom_product_template_attribute_value_ids")
    def _onchange_attribute_value_ids(self):
        if self.bom_product_template_attribute_value_ids:
            self.check_variants_validity()

    def check_variants_validity(self):
        if (
            not self.bom_product_template_attribute_value_ids
            or not self.component_template_id
        ):
            return
        variant_attr_ids = self.bom_product_template_attribute_value_ids.mapped(
            "attribute_id"
        )
        same_attrs = set(self.match_on_attribute_ids.ids) & set(variant_attr_ids.ids)
        if len(same_attrs) > 0:
            raise ValidationError(
                _(
                    "You cannot use an attribute value for attribute"
                    " %s in the field “Apply on Variants” as it’s the"
                    " same attribute used in field “Match on Attribute”"
                    "related to the component %s."
                    % (
                        self.env["product.attribute"].browse(same_attrs),
                        self.component_template_id.name,
                    )
                )
            )

    def write(self, vals):
        super(MrpBomLine, self).write(vals)


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    # flake8: noqa: C901
    def explode(self, product, quantity, picking_type=False):
        # Had to replace this method
        """
        Explodes the BoM and creates two lists with all the information you need:
        bom_done and line_done
        Quantity describes the number of times you need the BoM: so the quantity
        divided by the number created by the BoM
        and converted into its UoM
        """
        from collections import defaultdict

        graph = defaultdict(list)
        V = set()

        def check_cycle(v, visited, recStack, graph):
            visited[v] = True
            recStack[v] = True
            for neighbour in graph[v]:
                if visited[neighbour] is False:
                    if check_cycle(neighbour, visited, recStack, graph) is True:
                        return True
                elif recStack[neighbour] is True:
                    return True
            recStack[v] = False
            return False

        product_ids = set()
        product_boms = {}

        def update_product_boms():
            products = self.env["product.product"].browse(product_ids)
            product_boms.update(
                self._get_product2bom(
                    products,
                    bom_type="phantom",
                    picking_type=picking_type or self.picking_type_id,
                    company_id=self.company_id.id,
                )
            )
            # Set missing keys to default value
            for product in products:
                product_boms.setdefault(product, self.env["mrp.bom"])

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
        V |= {product.product_tmpl_id.id}

        bom_lines = []
        for bom_line in self.bom_line_ids:
            product_id = bom_line.product_id
            V |= {product_id.product_tmpl_id.id}
            graph[product.product_tmpl_id.id].append(product_id.product_tmpl_id.id)
            bom_lines.append((bom_line, product, quantity, False))
            product_ids.add(product_id.id)
        update_product_boms()
        product_ids.clear()
        while bom_lines:
            current_line, current_product, current_qty, parent_line = bom_lines[0]
            bom_lines = bom_lines[1:]

            if current_line._skip_bom_line(current_product):
                continue

            line_quantity = current_qty * current_line.product_qty
            if current_line.product_id not in product_boms:
                update_product_boms()
                product_ids.clear()
            # upd start
            component_template_product = self.get_component_template_product(
                current_line, product, current_line.product_id
            )
            if component_template_product:
                # need to set product_id temporary
                if current_line.product_id != component_template_product:
                    current_line.product_id = component_template_product
            else:
                # component_template_id is set, but no attribute value match.
                continue
            # upd end
            bom = product_boms.get(current_line.product_id)
            if bom:
                converted_line_quantity = current_line.product_uom_id._compute_quantity(
                    line_quantity / bom.product_qty, bom.product_uom_id
                )
                bom_lines += [
                    (
                        line,
                        current_line.product_id,
                        converted_line_quantity,
                        current_line,
                    )
                    for line in bom.bom_line_ids
                ]
                for bom_line in bom.bom_line_ids:
                    graph[current_line.product_id.product_tmpl_id.id].append(
                        bom_line.product_id.product_tmpl_id.id
                    )
                    if bom_line.product_id.product_tmpl_id.id in V and check_cycle(
                        bom_line.product_id.product_tmpl_id.id,
                        {key: False for key in V},
                        {key: False for key in V},
                        graph,
                    ):
                        raise UserError(
                            _(
                                "Recursion error!  A product with a Bill of Material "
                                "should not have itself in its BoM or child BoMs!"
                            )
                        )
                    V |= {bom_line.product_id.product_tmpl_id.id}
                    if bom_line.product_id not in product_boms:
                        product_ids.add(bom_line.product_id.id)
                boms_done.append(
                    (
                        bom,
                        {
                            "qty": converted_line_quantity,
                            "product": current_product,
                            "original_qty": quantity,
                            "parent_line": current_line,
                        },
                    )
                )
            else:
                # We round up here because the user expects
                # that if he has to consume a little more, the whole UOM unit
                # should be consumed.
                rounding = current_line.product_uom_id.rounding
                line_quantity = float_round(
                    line_quantity, precision_rounding=rounding, rounding_method="UP"
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

    def get_component_template_product(self, bom_line, bom_product_id, line_product_id):
        if bom_line.component_template_id:
            comp = bom_line.component_template_id
            comp_attr_ids = (
                comp.valid_product_template_attribute_line_ids.attribute_id.ids
            )
            prod_attr_ids = (
                bom_product_id.valid_product_template_attribute_line_ids.attribute_id.ids
            )
            # check attributes
            if not all(item in prod_attr_ids for item in comp_attr_ids):
                _log.info(
                    "Component skipped. Component attributes must be included into "
                    "product attributes to use component_template_id."
                )
                return False
            # find matching combination
            combination = self.env["product.template.attribute.value"]
            for ptav in bom_product_id.product_template_attribute_value_ids:
                combination |= self.env["product.template.attribute.value"].search(
                    [
                        ("product_tmpl_id", "=", comp.id),
                        ("attribute_id", "=", ptav.attribute_id.id),
                        (
                            "product_attribute_value_id",
                            "=",
                            ptav.product_attribute_value_id.id,
                        ),
                    ]
                )
            if len(combination) == 0:
                return False
            product_id = comp._get_variant_for_combination(combination)
            if product_id and product_id.active:
                return product_id
            return False
        else:
            return line_product_id

    def write(self, vals):
        res = super(MrpBom, self).write(vals)
        for line in self.bom_line_ids:
            line.update_component_attributes()
        return res
