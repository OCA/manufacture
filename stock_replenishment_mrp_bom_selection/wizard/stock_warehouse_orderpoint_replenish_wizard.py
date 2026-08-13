# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class StockWarehouseOrderpointReplenishWizard(models.TransientModel):
    _name = "stock.warehouse.orderpoint.replenish.wizard"
    _description = "Stock warehouse orderpoint replenish wizard"

    orderpoint_id = fields.Many2one("stock.warehouse.orderpoint")
    qty_to_order = fields.Float(
        related="orderpoint_id.qty_to_order", digits="Product Unit"
    )
    product_id = fields.Many2one("product.product", related="orderpoint_id.product_id")
    product_tmpl_id = fields.Many2one(
        "product.template", related="product_id.product_tmpl_id"
    )
    product_uom_id = fields.Many2one("uom.uom", related="orderpoint_id.product_uom")
    total_qty_to_produce = fields.Float(
        compute="_compute_total_qty_to_produce",
        string="Total Quantity to Produce",
        digits="Product Unit",
    )
    qty_remaining_to_produce = fields.Float(
        compute="_compute_qty_remaining_to_produce",
        string="Quantity Remaining to Produce",
        digits="Product Unit",
    )
    bom_line_ids = fields.One2many(
        comodel_name="bom.line.wizard",
        inverse_name="wizard_id",
        compute="_compute_bom_line_ids",
        store=True,
        readonly=False,
    )

    @api.depends("bom_line_ids.qty_to_produce")
    def _compute_total_qty_to_produce(self):
        for wizard in self:
            wizard.total_qty_to_produce = sum(
                wizard.bom_line_ids.mapped("qty_to_produce")
            )

    @api.depends("total_qty_to_produce", "qty_to_order")
    def _compute_qty_remaining_to_produce(self):
        for wizard in self:
            wizard.qty_remaining_to_produce = (
                wizard.qty_to_order - wizard.total_qty_to_produce
            )

    @api.depends("orderpoint_id")
    def _compute_bom_line_ids(self):
        for wizard in self:
            boms = wizard.orderpoint_id._get_selectable_boms()
            wizard.bom_line_ids = [fields.Command.clear()] + [
                fields.Command.create({"bom_id": bom.id}) for bom in boms
            ]

    def action_confirm(self):
        self.ensure_one()
        orderpoint = self.orderpoint_id
        uom = orderpoint.product_uom
        if uom.is_zero(self.total_qty_to_produce):
            raise UserError(self.env._("Nothing to produce."))
        # Take a snapshot of everything we need *before* touching the orderpoint:
        # `qty_to_order` is related to the orderpoint, so the first write below
        # invalidates it and, in cascade, `qty_remaining_to_produce`.
        qty_remaining = self.qty_remaining_to_produce
        qty_to_order = self.qty_to_order
        qty_per_bom = [
            (line.bom_id, line.qty_to_produce)
            for line in self.bom_line_ids
            if uom.compare(line.qty_to_produce, 0) == 1
        ]
        if uom.compare(qty_remaining, 0) == -1:
            raise UserError(
                self.env._(
                    "You cannot produce more than the quantity to order (%(qty)s).",
                    qty=qty_to_order,
                )
            )
        for bom, qty_to_produce in qty_per_bom:
            # `qty_to_order` is a computed field with an inverse that only stores
            # the value in `qty_to_order_manual`, so write there directly to make
            # sure the procurement uses exactly the requested quantity.
            orderpoint.qty_to_order_manual = qty_to_produce
            orderpoint.bom_id = bom
            orderpoint._procure_orderpoint_confirm(company_id=self.env.company)
        orderpoint.bom_id = False
        orderpoint.qty_to_order_manual = qty_remaining
        return True


class BomLineWizard(models.TransientModel):
    _name = "bom.line.wizard"
    _description = "Manufacture BOM line"

    wizard_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint.replenish.wizard"
    )
    bom_id = fields.Many2one("mrp.bom", string="Bill of Materials")
    qty_to_produce = fields.Float(string="Quantity to produce", digits="Product Unit")
    max_production_qty = fields.Float(
        string="Maximum Production Quantity",
        compute="_compute_max_production_qty",
        digits="Product Unit",
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        related="bom_id.product_uom_id",
        readonly=True,
    )
    production_time = fields.Float(compute="_compute_production_time")

    def _get_availability_context(self):
        """Evaluate the raw material stock on the orderpoint location."""
        self.ensure_one()
        orderpoint = self.wizard_id.orderpoint_id
        context = {"company_id": orderpoint.company_id.id}
        if orderpoint.location_id:
            context["location"] = orderpoint.location_id.id
        return context

    @api.depends("bom_id")
    def _compute_max_production_qty(self):
        for line in self:
            bom = line.bom_id
            max_qty = 0.0
            if bom and bom.bom_line_ids:
                max_qty = float("inf")
                bom_lines = bom.bom_line_ids.with_context(
                    **line._get_availability_context()
                )
                for bom_line in bom_lines:
                    # Quantity of the component needed for one finished unit,
                    # expressed in the component's own unit of measure.
                    qty_per_unit = bom_line.product_uom_id._compute_quantity(
                        bom_line.product_qty / (bom.product_qty or 1.0),
                        bom_line.product_id.uom_id,
                        round=False,
                    )
                    if bom_line.product_id.uom_id.is_zero(qty_per_unit):
                        continue
                    max_qty = min(
                        max_qty, bom_line.product_id.qty_available / qty_per_unit
                    )
                max_qty = max(max_qty if max_qty != float("inf") else 0.0, 0.0)
            line.max_production_qty = max_qty

    @api.depends("bom_id")
    def _compute_production_time(self):
        for line in self:
            line.production_time = sum(line.bom_id.operation_ids.mapped("time_cycle"))

    def action_material_availability_popup(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Availability of raw materials"),
            "res_model": "material.availability.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_bom_id": self.bom_id.id,
                "default_replenish_wizard_id": self.wizard_id.id,
            },
        }
