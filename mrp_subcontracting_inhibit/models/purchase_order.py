# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    subcontracting_inhibit = fields.Boolean(string="Inhibit subcontracting")

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        """We need to inject the context to set the right price"""
        subcontracting_inhibit_value = False
        if values.get("route_ids"):
            subcontracting_inhibit_value = any(
                values.get("route_ids").mapped("subcontracting_inhibit")
            )
            product_id = product_id.with_context(
                subcontracting_inhibit=subcontracting_inhibit_value
            )
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        res.update({"subcontracting_inhibit": subcontracting_inhibit_value})
        return res

    @api.onchange("subcontracting_inhibit")
    def _onchange_subcontracting_inhibit(self):
        return self._onchange_quantity()

    def _onchange_quantity(self):
        """We need to inject the context to set the right price"""
        _self = self.with_context(subcontracting_inhibit=self.subcontracting_inhibit)
        return super(PurchaseOrderLine, _self)._onchange_quantity()
