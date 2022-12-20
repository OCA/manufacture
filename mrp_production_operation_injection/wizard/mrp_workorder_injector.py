# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class MrpWorkorderInjector(models.TransientModel):

    _name = "mrp.workorder.injector"
    _description = "Inject operation from BOM into workorders"

    production_id = fields.Many2one("mrp.production", required=True)
    bom_id = fields.Many2one("mrp.bom", related="production_id.bom_id")
    allowed_bom_operation_ids = fields.Many2many(
        "mrp.routing.workcenter", compute="_compute_allowed_bom_operation_ids"
    )
    production_workorder_ids = fields.Many2many(
        "mrp.workorder", compute="_compute_production_workorder_ids"
    )
    operation_id = fields.Many2one(
        "mrp.routing.workcenter", "New operation", required=True
    )
    workorder_id = fields.Many2one("mrp.workorder", "Previous workorder", required=True)

    @api.depends("bom_id", "bom_id.operation_ids")
    def _compute_allowed_bom_operation_ids(self):
        for wiz in self:
            bom_operations = wiz.bom_id.operation_ids
            # TODO: Move this check in default_get or somewhere else?
            if not wiz.bom_id or not bom_operations:
                wiz.allowed_bom_operation_ids = [fields.Command.clear()]
                continue
            # Filter out operations applying only for other variants
            allowed_operations = bom_operations.filtered(
                lambda o: not o._skip_operation_line(wiz.production_id.product_id)
            )
            # TODO: filter out operations consuming components?
            # AFAICS the link from bom line to operations will only be used to define
            # on the stock move in which workorder such component is supposed to be
            # consumed, and will then be used to compute the state of the workorder
            # through the reservation_state field of the MO:
            # - Waiting components if move is not assigned
            # - Ready if move is assigned
            wiz.allowed_bom_operation_ids = [fields.Command.set(allowed_operations.ids)]

    @api.depends("production_id")
    def _compute_production_workorder_ids(self):
        for wiz in self:
            prod_workorders = wiz.production_id.workorder_ids
            if not prod_workorders:
                wiz.production_workorder_ids = [fields.Command.clear()]
                continue
            done_wos = prod_workorders.filtered(lambda w: w.state == "done")
            if not done_wos or len(done_wos) == 1:
                wiz.production_workorder_ids = [fields.Command.set(prod_workorders.ids)]
                continue
            # Only allow to add new operation after last Done workorder
            last_done_wo = fields.first(done_wos.sorted(reverse=True))
            allowed_wos = last_done_wo + prod_workorders.filtered(
                lambda w: w.state != "done"
            )
            wiz.production_workorder_ids = allowed_wos

    def action_add_operation(self):
        self.ensure_one()
        self.production_id._add_workorder(self.operation_id, self.workorder_id)
        return {"type": "ir.actions.act_window_close"}
