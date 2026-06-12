# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_compare


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    bom_synchronization_group_id = fields.Many2one(
        comodel_name="mrp.bom.synchronization.group",
        string="Synchronization Group",
        ondelete="set null",
    )
    bom_sync_out_of_sync = fields.Boolean(
        string="Components Out of Sync",
        related="bom_synchronization_group_id.out_of_sync",
    )

    def _get_component_key(self, line):
        return (
            line.product_id.id,
            frozenset(line.bom_product_template_attribute_value_ids.ids),
        )

    def _get_component_diff(self, target):
        self.ensure_one()
        diff = []
        remaining = list(target.bom_line_ids)
        for ref_line in self.bom_line_ids:
            key = self._get_component_key(ref_line)
            match = next(
                (line for line in remaining if self._get_component_key(line) == key),
                None,
            )
            if match:
                remaining.remove(match)
                rounding = ref_line.product_uom_id.rounding
                qty_changed = float_compare(
                    match.product_qty,
                    ref_line.product_qty,
                    precision_rounding=rounding,
                )
                if qty_changed != 0 or match.product_uom_id != ref_line.product_uom_id:
                    diff.append(
                        {
                            "change_type": "update",
                            "product_id": ref_line.product_id,
                            "target_line": match,
                            "current_qty": match.product_qty,
                            "new_qty": ref_line.product_qty,
                            "current_uom_id": match.product_uom_id,
                            "new_uom_id": ref_line.product_uom_id,
                            "ref_line": ref_line,
                        }
                    )
            else:
                diff.append(
                    {
                        "change_type": "add",
                        "product_id": ref_line.product_id,
                        "target_line": False,
                        "current_qty": 0.0,
                        "new_qty": ref_line.product_qty,
                        "current_uom_id": self.env["uom.uom"],
                        "new_uom_id": ref_line.product_uom_id,
                        "ref_line": ref_line,
                    }
                )
        for line in remaining:
            diff.append(
                {
                    "change_type": "remove",
                    "product_id": line.product_id,
                    "target_line": line,
                    "current_qty": line.product_qty,
                    "new_qty": 0.0,
                    "current_uom_id": line.product_uom_id,
                    "new_uom_id": self.env["uom.uom"],
                    "ref_line": False,
                }
            )
        return diff

    def _get_synced_operation(self, ref_line, target_bom):
        # Hook to resolve which operation of ``target_bom`` should be assigned
        # to the synchronized component line. The base module ignores
        # operations and returns an empty recordset, so added lines get no
        # operation and updated lines keep their own. Override in a custom
        # module to implement a matching strategy (e.g. by operation name).
        return self.env["mrp.routing.workcenter"]

    def _get_synced_line_values(self, ref_line, target_bom):
        return {
            "product_id": ref_line.product_id.id,
            "product_qty": ref_line.product_qty,
            "product_uom_id": ref_line.product_uom_id.id,
            "bom_product_template_attribute_value_ids": [
                (6, 0, ref_line.bom_product_template_attribute_value_ids.ids)
            ],
            "operation_id": self._get_synced_operation(ref_line, target_bom).id,
        }

    def _synchronize_components_to(self, targets):
        self.ensure_one()
        for target in targets:
            if target == self:
                continue
            commands = []
            for entry in self._get_component_diff(target):
                if entry["change_type"] == "remove":
                    commands.append((2, entry["target_line"].id))
                elif entry["change_type"] == "add":
                    commands.append(
                        (0, 0, self._get_synced_line_values(entry["ref_line"], target))
                    )
                else:
                    vals = {
                        "product_qty": entry["new_qty"],
                        "product_uom_id": entry["new_uom_id"].id,
                    }
                    operation = self._get_synced_operation(entry["ref_line"], target)
                    if operation:
                        vals["operation_id"] = operation.id
                    commands.append((1, entry["target_line"].id, vals))
            if commands:
                target.with_context(skip_bom_component_sync=True).write(
                    {"bom_line_ids": commands}
                )

    def _propagate_components_to_group(self):
        for bom in self:
            group = bom.bom_synchronization_group_id
            if not group or group.synchronization_mode != "auto":
                continue
            bom._synchronize_components_to(group.bom_ids - bom)
