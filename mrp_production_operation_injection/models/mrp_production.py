# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    display_inject_workorder = fields.Boolean(
        compute="_compute_display_inject_workorder"
    )

    @api.depends("state", "bom_id", "bom_id.operation_ids", "workorder_ids")
    def _compute_display_inject_workorder(self):
        for production in self:
            production.display_inject_workorder = (
                production.state in ["confirmed", "progress", "to_close"]
                and production.bom_id.operation_ids
                and production.workorder_ids
            )

    def action_open_workorder_injector(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp_production_operation_injection.mrp_workorder_injector_action"
        )
        ctx = self.env.context.copy()
        ctx["default_production_id"] = self.id
        action.update({"context": ctx})
        return action

    def _prepare_injected_workorder_values(self, operation):
        self.ensure_one()
        return {
            "name": operation.name,
            "production_id": self.id,
            "workcenter_id": operation.workcenter_id.id,
            "product_uom_id": self.product_uom_id.id,
            "operation_id": operation.id,
            "state": "pending",
        }

    def _add_workorder(self, operation, previous_workorder):
        self.ensure_one()
        following_workorders = self.workorder_ids.filtered(
            lambda w: w.sequence > previous_workorder.sequence
        )
        next_workorder = fields.first(following_workorders)
        # Prepare creation of new workorder
        workorder_values = self._prepare_injected_workorder_values(operation)
        workorder_values["sequence"] = previous_workorder.sequence + 1
        workorder_values["next_work_order_id"] = next_workorder.id
        # FIXME: state computation is not good in Odoo anyway so handle
        #  only most 'probable' cases only
        if next_workorder.state in ["ready", "progress"]:
            workorder_values["state"] = "ready"
        # Update following workorders sequence before create to make sure workorders
        #  can be ordered properly for _action_confirm (cf override in mrp_workorder)
        for wo in following_workorders:
            wo.sequence += 1
        new_workorder = self.env["mrp.workorder"].create(workorder_values)
        # Update next workorder
        # FIXME: state computation is not good in Odoo anyway so handle
        #  only most 'probable' cases only
        if next_workorder.state == "ready":
            next_workorder.state = "pending"
        new_workorder.duration_expected = new_workorder._get_duration_expected()
        # Replan if needed after cache invalidation to make sure all workorders are considered
        self.invalidate_cache()
        if self.is_planned:
            self._plan_workorders(replan=True)
        return True
