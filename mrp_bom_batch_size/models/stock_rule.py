# Copyright 2025 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

from odoo import api, models
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def run(self, procurements, raise_user_error=True):
        """Override to implement batch size logic for manufacturing procurements"""
        # Get the original behavior for non-manufacturing procurements
        other_procurements = [p for p in procurements if p.rule.action != "manufacture"]
        if other_procurements:
            super().run(other_procurements, raise_user_error)

        # Handle manufacturing procurements with batch size logic
        manufacturing_procurements = [
            p for p in procurements if p.rule.action == "manufacture"
        ]
        if not manufacturing_procurements:
            return

        new_productions_values_by_company = {}
        for procurement in manufacturing_procurements:
            company = procurement.company_id
            if company not in new_productions_values_by_company:
                new_productions_values_by_company[company] = {
                    "values": [],
                    "procurements": [],
                }

            if procurement.product_qty <= 0:
                # If procurement contains negative quantity,
                #  don't create a MO that would be for a negative value.
                continue

            bom = procurement.rule._get_matching_bom(
                procurement.product_id, procurement.company_id, procurement.values
            )
            mo = self.env["mrp.production"]
            if procurement.origin != "MPS":
                domain = procurement.rule._make_mo_get_domain(procurement, bom)
                mo = self.env["mrp.production"].sudo().search(domain, limit=1)

            is_batch_size = bom and bom.enable_batch_size
            if not mo or is_batch_size:
                procurement_qty = procurement.product_qty
                batch_size = (
                    bom.product_uom_id._compute_quantity(
                        bom.batch_size, procurement.product_uom
                    )
                    if is_batch_size
                    else procurement_qty
                )
                vals = procurement.rule._prepare_mo_vals(
                    procurement_qty,
                    procurement.product_uom,
                    procurement.product_id,
                    procurement.location_id,
                    procurement.name,
                    procurement.origin,
                    procurement.company_id,
                    procurement.values,
                    bom,
                )
                while (
                    float_compare(
                        procurement_qty,
                        0,
                        precision_rounding=procurement.product_uom.rounding,
                    )
                    > 0
                ):
                    actual_batch_size = min(batch_size, procurement_qty)
                    new_productions_values_by_company[company]["values"].append(
                        {
                            **vals,
                            "product_qty": procurement.product_uom._compute_quantity(
                                actual_batch_size, bom.product_uom_id
                            )
                            if bom
                            else actual_batch_size,
                        }
                    )
                    new_productions_values_by_company[company]["procurements"].append(
                        procurement
                    )
                    procurement_qty -= actual_batch_size

        # Create the manufacturing orders
        for company, production_data in new_productions_values_by_company.items():
            productions = (
                self.env["mrp.production"]
                .sudo()
                .with_company(company)
                .create(production_data["values"])
            )
            # Auto-confirm the productions if needed
            for production, procurement in zip(
                productions, production_data["procurements"], strict=True
            ):
                try:
                    procurement._post_production(production)
                except Exception as e:
                    _logger.warning(
                        "Failed to post production %s: %s", production.id, str(e)
                    )

        return True
