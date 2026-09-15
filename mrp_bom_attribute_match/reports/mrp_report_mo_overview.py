# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.mrp.report.mrp_report_mo_overview import (
    ReportMrpReport_Mo_Overview,
)


@api.model
def _get_report_data(self, production_id):
    # Override this function to resolve dynamic component templates to a
    # product variant before the `missing_components` cost roll-up. After
    # `mrp.production.action_confirm()` the OCA override clears `product_id`
    # on every BOM line that has a `component_template_id`, so the standard
    # MO Overview crashes with `Expected singleton: uom.uom()` because
    # `line.product_id` is empty.
    production = self.env["mrp.production"].browse(production_id)
    # Necessary to fetch the right quantities for multi-warehouse
    production = production.with_context(warehouse_id=production.warehouse_id.id)

    components = self._get_components_data(production, level=1, current_index="")
    operations = self._get_operations_data(production, level=1, current_index="")
    initial_mo_cost, initial_bom_cost, initial_real_cost = self._compute_cost_sums(
        components, operations
    )

    if production.bom_id:
        currency = (production.company_id or self.env.company).currency_id
        current_bom_lines = (
            production.move_raw_ids.bom_line_id
            | self._get_kit_bom_lines(production.bom_id)
        )
        missing_components = production.bom_id.bom_line_ids.filtered(
            lambda bom_line: bom_line not in current_bom_lines
            and not bom_line._skip_bom_line(production.product_id)
        )
        missing_operations = (
            bom_line
            for bom_line in production.bom_id.operation_ids
            if bom_line not in production.workorder_ids.operation_id
        )
        for line in missing_components:
            # vvvvvvvvvvvvvvv START CHANGES vvvvvvvvvvvvvvv
            # Custom code: resolve dynamic component template to a product
            # variant. Falls back to `line.product_id` when no template is set.
            line_product = line.product_id
            if line.component_template_id and not line_product:
                line_product = production.bom_id._get_component_template_product(
                    line, production.product_id, line.product_id
                )
            if not line_product:
                # Component template has no matching active variant for this
                # MO's attribute combination — drop from the cost roll-up
                # rather than crash.
                continue
            # ^^^^^^^^^^^^^^^^^^^ END CHANGES ^^^^^^^^^^^^^^^^^^^
            line_cost = (
                line_product.uom_id._compute_price(
                    line_product.standard_price, line.product_uom_id
                )
                * line.product_qty
            )
            initial_bom_cost += currency.round(
                line_cost * production.product_uom_qty / production.bom_id.product_qty
            )
        for operation in missing_operations:
            cost = operation.with_context(
                product=production.product_id,
                quantity=production.product_qty,
                unit=production.product_uom_id,
            ).cost
            bom_cost = self.env.company.currency_id.round(cost)
            initial_bom_cost += currency.round(
                bom_cost * production.product_uom_qty / production.bom_id.product_qty
            )

    remaining_cost_share, byproducts = self._get_byproducts_data(
        production,
        initial_mo_cost,
        initial_bom_cost,
        initial_real_cost,
        level=1,
        current_index="",
    )
    summary = self._get_mo_summary(
        production,
        components,
        operations,
        initial_mo_cost,
        initial_bom_cost,
        initial_real_cost,
        remaining_cost_share,
    )
    extra_lines = self._get_report_extra_lines(
        summary, components, operations, production
    )
    return {
        "id": production.id,
        "name": production.display_name,
        "summary": summary,
        "components": components,
        "operations": operations,
        "byproducts": byproducts,
        "extras": extra_lines,
        "cost_breakdown": self._get_cost_breakdown_data(
            production, extra_lines, remaining_cost_share
        ),
    }


ReportMrpReport_Mo_Overview._get_report_data = _get_report_data
