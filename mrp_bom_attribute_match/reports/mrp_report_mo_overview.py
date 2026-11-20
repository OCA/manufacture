# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ReportMrpReportMoOverview(models.AbstractModel):
    _inherit = "report.mrp.report_mo_overview"

    @api.model
    def _get_report_data(self, production_id):
        production = self.env["mrp.production"].browse(production_id)
        production = production.with_context(warehouse_id=production.warehouse_id.id)

        components = self._get_components_data(production, level=1, current_index="")
        operations = self._get_operations_data(production, level=1, current_index="")
        initial_mo_cost = self._get_mo_cost_sum(components, operations)

        if production.bom_id:
            currency = (production.company_id or self.env.company).currency_id
            current_bom_lines = production.move_raw_ids.bom_line_id
            missing_components = production.bom_id.bom_line_ids.filtered(
                lambda bom_line: (
                    bom_line not in current_bom_lines
                    and not bom_line._skip_bom_line(production.product_id)
                )
            )

            bom_quantity = production.uom_id._compute_quantity(
                production.product_qty, production.bom_id.uom_id
            )
            for line in missing_components:
                line_product = line.product_id
                if line.component_template_id and not line_product:
                    line_product = production.bom_id._get_component_template_product(
                        line, production.product_id, line.product_id
                    )
                if not line_product:
                    continue
                line_cost = (
                    line_product.uom_id._compute_price(
                        line_product.standard_price, line.uom_id
                    )
                    * line.product_qty
                )
                initial_mo_cost += currency.round(
                    line_cost * bom_quantity / production.bom_id.product_qty
                )

            for operation in production.bom_id.operation_ids:
                if operation in production.workorder_ids.operation_id:
                    continue
                cost = operation.with_context(
                    product=production.product_id,
                    quantity=production.product_qty,
                    unit=production.uom_id,
                ).cost
                operation_cost = currency.round(cost)
                initial_mo_cost += currency.round(
                    operation_cost * bom_quantity / production.bom_id.product_qty
                )

        remaining_cost_share, byproducts = self._get_byproducts_data(
            production,
            initial_mo_cost,
            level=1,
            current_index="",
        )
        summary = self._get_mo_summary(
            production,
            components,
            initial_mo_cost,
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
