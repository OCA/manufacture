# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class MrpBomSynchronizationWizard(models.TransientModel):
    _name = "mrp.bom.synchronization.wizard"
    _description = "BoM Synchronization Wizard"

    group_id = fields.Many2one(
        comodel_name="mrp.bom.synchronization.group",
        string="Synchronization Group",
        required=True,
    )
    reference_bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Reference BoM",
        domain="[('bom_synchronization_group_id', '=', group_id)]",
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name="mrp.bom.synchronization.wizard.line",
        inverse_name="wizard_id",
        string="Planned Changes",
        compute="_compute_line_ids",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        group_id = self.env.context.get("default_group_id")
        if group_id and not res.get("reference_bom_id"):
            group = self.env["mrp.bom.synchronization.group"].browse(group_id)
            res["reference_bom_id"] = group.bom_ids[:1].id
        return res

    @api.depends("reference_bom_id")
    def _compute_line_ids(self):
        for wizard in self:
            commands = [(5, 0, 0)]
            reference = wizard.reference_bom_id
            if reference:
                for target in wizard.group_id.bom_ids - reference:
                    for entry in reference._get_component_diff(target):
                        commands.append(
                            (
                                0,
                                0,
                                {
                                    "target_bom_id": target.id,
                                    "product_id": entry["product_id"].id,
                                    "change_type": entry["change_type"],
                                    "current_qty": entry["current_qty"],
                                    "new_qty": entry["new_qty"],
                                    "current_uom_id": entry["current_uom_id"].id,
                                    "new_uom_id": entry["new_uom_id"].id,
                                },
                            )
                        )
            wizard.line_ids = commands

    def action_synchronize(self):
        self.ensure_one()
        if not self.reference_bom_id:
            raise UserError(self.env._("Please select a reference BoM."))
        self.reference_bom_id._synchronize_components_to(
            self.group_id.bom_ids - self.reference_bom_id
        )
        return {"type": "ir.actions.act_window_close"}


class MrpBomSynchronizationWizardLine(models.TransientModel):
    _name = "mrp.bom.synchronization.wizard.line"
    _description = "BoM Synchronization Wizard Line"

    wizard_id = fields.Many2one(
        comodel_name="mrp.bom.synchronization.wizard",
        required=True,
        ondelete="cascade",
    )
    target_bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Bill of Materials",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Component",
    )
    change_type = fields.Selection(
        selection=[
            ("add", "Add"),
            ("remove", "Remove"),
            ("update", "Update"),
        ],
        string="Change",
    )
    current_qty = fields.Float(
        digits="Product Unit of Measure",
    )
    new_qty = fields.Float(
        digits="Product Unit of Measure",
    )
    current_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Current UoM",
    )
    new_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="New UoM",
    )
