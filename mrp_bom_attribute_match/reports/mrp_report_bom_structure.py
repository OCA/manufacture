# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools import float_round


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        # OVERRIDE to fill in the `line.product_id` if a component template is used.
        # To avoid a complete override, we HACK the bom by replacing it with a virtual
        # record, and modifying it's lines on-the-fly.
        has_template_lines = any(
            line.component_template_id for line in bom.bom_line_ids
        )
        if has_template_lines:
            bom = bom.new(origin=bom)
            to_ignore_line_ids = []
            for line in bom.bom_line_ids:
                if line._skip_bom_line(product) or not line.component_template_id:
                    continue
                line_product = bom._get_component_template_product(
                    line, product, line.product_id
                )
                if not line_product:
                    to_ignore_line_ids.append(line.id)
                    continue
                else:
                    line.product_id = line_product
            if to_ignore_line_ids:
                for to_ignore_line_id in to_ignore_line_ids:
                    bom.bom_line_ids = [(3, to_ignore_line_id, 0)]
        components, total = super()._get_bom_lines(
            bom, bom_quantity, product, line_id, level
        )
        # Replace any NewId value by the real record id
        # Otherwise it's evaluated as False in some situations, and it may cause issues
        if has_template_lines:
            for component in components:
                for key, value in component.items():
                    if isinstance(value, models.NewId):
                        component[key] = value.origin
        return components, total

    def _get_price(self, bom, factor, product):
        """Replaced in order to implement component_template logic"""
        price = 0
        if bom.operation_ids:
            # routing are defined on a BoM and don't have a concept of quantity.
            # It means that the operation time are defined for the quantity on
            # the BoM (the user produces a batch of products). E.g the user
            # product a batch of 10 units with a 5 minutes operation, the time
            # will be the 5 for a quantity between 1-10, then doubled for
            # 11-20,...
            operation_cycle = float_round(
                factor, precision_rounding=1, rounding_method="UP"
            )
            operations = self._get_operation_line(bom, operation_cycle, 0)
            price += sum([op["total"] for op in operations])

        for line in bom.bom_line_ids:
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = line.product_uom_id._compute_quantity(
                    line.product_qty * (factor / bom.product_qty),
                    line.child_bom_id.product_uom_id,
                )
                sub_price = self._get_price(line.child_bom_id, qty, line.product_id)
                price += sub_price
            else:
                prod_qty = line.product_qty * factor / bom.product_qty
                company = bom.company_id or self.env.company
                # Modification start
                if line.component_template_id:
                    vals = product.product_template_attribute_value_ids.mapped(
                        "product_attribute_value_id"
                    ).ids
                    match_found = False
                    for prod in line.component_template_id.product_variant_ids:
                        pavs = prod.product_template_attribute_value_ids.mapped(
                            "product_attribute_value_id"
                        )
                        match = set(pavs.ids).issubset(set(vals))
                        if match:
                            match_found = True
                            break
                    if match_found:
                        not_rounded_price = (
                            prod.uom_id._compute_price(
                                prod.with_company(company).standard_price,
                                line.product_uom_id,
                            )
                            * prod_qty
                        )
                        price += company.currency_id.round(not_rounded_price)
                    else:
                        continue
                    # Modification end
                else:
                    not_rounded_price = (
                        line.product_id.uom_id._compute_price(
                            line.product_id.with_company(company).standard_price,
                            line.product_uom_id,
                        )
                        * prod_qty
                    )
                    price += company.currency_id.round(not_rounded_price)
        return price
