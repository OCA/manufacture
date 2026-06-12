# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpBomSynchronizationGroup(models.Model):
    _name = "mrp.bom.synchronization.group"
    _description = "BoM Synchronization Group"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    bom_ids = fields.One2many(
        comodel_name="mrp.bom",
        inverse_name="bom_synchronization_group_id",
        string="Bills of Materials",
        check_company=True,
    )
    synchronization_mode = fields.Selection(
        selection=[
            ("warning", "Warning and fix manually"),
            ("auto", "Synchronize automatically"),
        ],
        required=True,
        default=lambda self: self.env["ir.config_parameter"]
        .sudo()
        .get_param(
            "mrp_bom_synchronization_group.default_synchronization_mode",
            "warning",
        ),
        help="Synchronization behaviour for this group. New groups take the"
        " default defined in the Manufacturing settings; it can be changed per"
        " group.",
    )
    out_of_sync = fields.Boolean(
        compute="_compute_out_of_sync",
        store=True,
        help="The members of this group do not share the same components.",
    )
    discrepancy_summary = fields.Html(
        compute="_compute_discrepancy_summary",
    )

    @api.depends(
        "bom_ids",
        "bom_ids.bom_line_ids",
        "bom_ids.bom_line_ids.product_id",
        "bom_ids.bom_line_ids.product_qty",
        "bom_ids.bom_line_ids.product_uom_id",
        "bom_ids.bom_line_ids.bom_product_template_attribute_value_ids",
    )
    def _compute_out_of_sync(self):
        for group in self:
            boms = group.bom_ids
            if len(boms) < 2:
                group.out_of_sync = False
                continue
            reference = boms[0]
            group.out_of_sync = any(
                reference._get_component_diff(target) for target in boms[1:]
            )

    def _get_discrepancy_label(self, entry):
        if entry["change_type"] == "add":
            return self.env._("Missing component")
        if entry["change_type"] == "remove":
            return self.env._("Extra component")
        qty_changed = entry["current_qty"] != entry["new_qty"]
        uom_changed = entry["current_uom_id"] != entry["new_uom_id"]
        if qty_changed and uom_changed:
            return self.env._("Different quantity and unit of measure")
        if uom_changed:
            return self.env._("Different unit of measure")
        return self.env._("Different quantity")

    def _compute_discrepancy_summary(self):
        for group in self:
            baseline = group.bom_ids[:1]
            if not group.out_of_sync or not baseline:
                group.discrepancy_summary = False
                continue
            blocks = []
            for target in group.bom_ids - baseline:
                diff = baseline._get_component_diff(target)
                if not diff:
                    continue
                rows = "".join(
                    f"<li>{group._get_discrepancy_label(d)}: "
                    f"{d['product_id'].display_name}</li>"
                    for d in diff
                )
                blocks.append(f"<b>{target.display_name}</b><ul>{rows}</ul>")
            group.discrepancy_summary = "".join(blocks) if blocks else False

    def action_open_synchronization_wizard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_bom_synchronization_group." "mrp_bom_synchronization_wizard_action"
        )
        action["context"] = {"default_group_id": self.id}
        return action
