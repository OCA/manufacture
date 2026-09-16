# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpBomComponentMassChange(models.TransientModel):
    _name = "mrp.bom.component.mass.change"
    _description = "Mass Change BoM Component"

    component_id = fields.Many2one(
        "product.product", string="Component to Change", required=True
    )
    component_locked = fields.Boolean(default=False)
    change_type = fields.Selection(
        [("replace", "Replace"), ("remove", "Remove")],
        required=True,
        default="replace",
    )
    new_component_id = fields.Many2one("product.product", string="New Component")
    new_product_qty = fields.Float(
        string="New Quantity", digits="Product Unit of Measure", default=1.0
    )
    bom_ids = fields.Many2many(
        "mrp.bom",
        string="Bills of Materials",
        compute="_compute_bom_ids",
        store=True,
        readonly=False,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if (
            "component_id" in fields_list
            and not res.get("component_id")
            and self.env.context.get("active_model") == "mrp.bom.line"
        ):
            lines = self.env["mrp.bom.line"].browse(
                self.env.context.get("active_ids", [])
            )
            products = lines.product_id
            if len(products) == 1:
                res["component_id"] = products.id
        return res

    @api.onchange("change_type")
    def _onchange_change_type(self):
        if self.change_type == "remove":
            self.new_component_id = False

    @api.depends("component_id", "new_component_id")
    def _compute_bom_ids(self):
        for wizard in self:
            if not wizard.component_id:
                wizard.bom_ids = False
                continue
            boms = self.env["mrp.bom"].search(
                [("bom_line_ids.product_id", "=", wizard.component_id.id)]
            )
            if wizard.new_component_id:
                boms -= self.env["mrp.bom"].search(
                    [("bom_line_ids.product_id", "=", wizard.new_component_id.id)]
                )
            wizard.bom_ids = boms

    def action_apply(self):
        self.ensure_one()
        if self.change_type == "replace":
            if not self.new_component_id:
                raise UserError(_("You must select the new component."))
            if self.new_component_id == self.component_id:
                raise UserError(
                    _(
                        "The new component must be different from the "
                        "component to change."
                    )
                )
            if self.new_product_qty <= 0:
                raise UserError(_("You must set the new quantity."))
        if not self.bom_ids:
            raise UserError(_("You must select at least one bill of materials."))
        lines = self.bom_ids.bom_line_ids.filtered(
            lambda line: line.product_id == self.component_id
        )
        if self.change_type == "remove":
            lines.unlink()
        else:
            for line in lines:
                vals = {
                    "product_id": self.new_component_id.id,
                    "product_qty": self.new_product_qty,
                }
                if (
                    line.product_uom_id.category_id
                    != self.new_component_id.uom_id.category_id
                ):
                    vals["product_uom_id"] = self.new_component_id.uom_id.id
                line.write(vals)
        return {"type": "ir.actions.act_window_close"}
