# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# - Héctor Villarreal <hector.villarreal@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        domain = super()._make_po_get_domain(company_id, values, partner)
        if isinstance(domain, list):
            domain = tuple(domain)
        currency_id = values.get("currency_id")
        if currency_id:
            domain = tuple(domain) + (("currency_id", "=", currency_id),)
        return domain

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)

        currency_id = False
        if isinstance(values, dict):
            currency_id = values.get("currency_id")
        elif isinstance(values, (list, tuple)):
            for v in values:
                if isinstance(v, dict) and v.get("currency_id"):
                    currency_id = v.get("currency_id")
                    break

        if currency_id:
            res["currency_id"] = currency_id
        return res

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
        bom,
    ):
        res = super()._prepare_mo_vals(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
            bom,
        )
        if "planned_order_id" in values:
            res["planned_order_id"] = values["planned_order_id"]
        return res
