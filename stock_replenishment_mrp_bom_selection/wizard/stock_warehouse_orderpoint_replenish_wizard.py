# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockWarehouseOrderpointReplenishWizard(models.TransientModel):
    _name = "stock.warehouse.orderpoint.replenish.wizard"
    _description = "Stock warehouse orderpoint replenish wizard"

    orderpoint_id = fields.Many2one("stock.warehouse.orderpoint")
    qty_to_order = fields.Float(related="orderpoint_id.qty_to_order")
    product_id = fields.Many2one("product.product", related="orderpoint_id.product_id")
    product_tmpl_id = fields.Many2one(
        "product.template", related="product_id.product_tmpl_id"
    )
    total_qty_to_produce = fields.Float(
        compute="_compute_total_qty_to_produce",
        string="Total Quantity to Produce",
    )
    qty_remaining_to_produce = fields.Float(
        compute="_compute_qty_remaining_to_produce",
        string="Quantity Remaining to Produce",
        store=True,
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
        self.bom_line_ids = None
        lines_vals = []
        boms = self.product_id.bom_ids.filtered(
            lambda x: not x.product_id or x.product_id == self.product_id
        )
        for line in boms:
            lines_vals.append(
                (
                    0,
                    0,
                    {
                        "wizard_id": self.id,
                        "bom_id": line.id,
                    },
                )
            )
        self.bom_line_ids = lines_vals

    def action_confirm(self):
        pd = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        if float_is_zero(self.total_qty_to_produce, precision_digits=pd):
            raise UserError(_("Nothing to produce."))
        for line in self.bom_line_ids.filtered(lambda x: x.qty_to_produce > 0):
            self.orderpoint_id.qty_to_order = line.qty_to_produce
            self.orderpoint_id.bom_id = line.bom_id
            self.orderpoint_id._procure_orderpoint_confirm(company_id=self.env.company)
        self.orderpoint_id.bom_id = False
        self.orderpoint_id.qty_to_order = self.qty_remaining_to_produce
        return True


class BomLineWizard(models.TransientModel):
    _name = "bom.line.wizard"
    _description = "Manufacture BOM line"

    wizard_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint.replenish.wizard"
    )
    bom_id = fields.Many2one("mrp.bom", string="Bill of Materials")
    qty_to_produce = fields.Float(string="Quantity to produce")
    max_production_qty = fields.Float(
        string="Maximum Production Quantity", compute="_compute_max_production_qty"
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        related="bom_id.product_tmpl_id.uom_id",
        readonly=True,
    )
    production_time = fields.Float(compute="_compute_production_time")

    @api.depends("bom_id")
    def _compute_max_production_qty(self):
        for line in self:
            max_qty = float("inf")
            for bom_line in line.bom_id.bom_line_ids:
                available_qty = bom_line.product_id.qty_available / bom_line.product_qty
                if available_qty < 0:
                    max_qty = 0
                    break
                max_qty = min(max_qty, available_qty)
            line.max_production_qty = max_qty

    @api.depends("bom_id")
    def _compute_production_time(self):
        for line in self:
            production_time = sum(
                operation.time_cycle for operation in line.bom_id.operation_ids
            )
            line.production_time = production_time

    def action_material_availability_popup(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Availability of raw materials",
            "res_model": "material.availability.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_bom_id": self.bom_id.id,
                "default_replenish_wizard_id": self.wizard_id.id,
            },
        }
