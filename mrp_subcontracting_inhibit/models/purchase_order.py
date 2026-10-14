# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    subcontracting_inhibit = fields.Boolean(string="Inhibit subcontracting")

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
        po,
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
            product_id=product_id,
            product_qty=product_qty,
            product_uom=product_uom,
            location_dest_id=location_dest_id,
            name=name,
            origin=origin,
            company_id=company_id,
            values=values,
            po=po,
        )
        res.update({"subcontracting_inhibit": subcontracting_inhibit_value})
        return res

    @api.onchange("subcontracting_inhibit")
    def _onchange_subcontracting_inhibit(self):
        self._onchange_quantity()

    def _onchange_quantity(self):
        """We need to inject the context to set the right price"""
        self.with_context(
            subcontracting_inhibit=self.subcontracting_inhibit
        )._compute_price_unit_and_date_planned_and_name()
