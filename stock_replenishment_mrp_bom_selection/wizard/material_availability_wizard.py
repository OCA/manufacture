# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MaterialAvailabilityWizard(models.TransientModel):
    _name = "material.availability.wizard"
    _description = "Material Availability Wizard"

    replenish_wizard_id = fields.Many2one("stock.warehouse.orderpoint.replenish.wizard")
    bom_id = fields.Many2one("mrp.bom", string="Bill of Materials")
    product_ids = fields.One2many(
        comodel_name="material.availability.wizard.line",
        inverse_name="wizard_id",
        string="Products",
        compute="_compute_product_ids",
        store=True,
        readonly=False,
    )

    @api.depends("bom_id")
    def _compute_product_ids(self):
        for wizard in self:
            # Show the stock of the location being replenished, not the whole company
            orderpoint = wizard.replenish_wizard_id.orderpoint_id
            context = {"company_id": orderpoint.company_id.id}
            if orderpoint.location_id:
                context["location"] = orderpoint.location_id.id
            wizard.product_ids = [fields.Command.clear()] + [
                fields.Command.create(
                    {
                        "product_id": line.product_id.id,
                        "product_qty_available": line.product_id.with_context(
                            **context
                        ).qty_available,
                    }
                )
                for line in wizard.bom_id.bom_line_ids
            ]

    def action_close(self):
        self.ensure_one()
        return {
            "name": self.env._("Replenish"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.warehouse.orderpoint.replenish.wizard",
            "res_id": self.replenish_wizard_id.id,
            "target": "new",
            "context": {
                "default_orderpoint_id": self.replenish_wizard_id.orderpoint_id.id
            },
        }


class MaterialAvailabilityWizardLine(models.TransientModel):
    _name = "material.availability.wizard.line"
    _description = "Material Availability Wizard Line"

    wizard_id = fields.Many2one("material.availability.wizard")
    product_id = fields.Many2one("product.product", string="Product")
    product_uom_id = fields.Many2one(
        "uom.uom", related="product_id.uom_id", string="Unit"
    )
    product_qty_available = fields.Float(
        string="Quantity Available", digits="Product Unit"
    )
