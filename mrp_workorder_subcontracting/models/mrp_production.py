from odoo import _, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    subcontract_purchase_order_count = fields.Integer(
        string="Subcontract Purchase Orders",
        compute="_compute_subcontract_counts",
    )
    subcontract_moves_count = fields.Integer(
        string="Subcontract Moves",
        compute="_compute_subcontract_counts",
    )

    def _compute_subcontract_counts(self):
        for production in self:
            workorders = production.workorder_ids.filtered("subcontract_ok")
            production.subcontract_purchase_order_count = len(
                workorders.purchase_order_line_ids.order_id
            )
            production.subcontract_moves_count = len(
                workorders.delivery_move_ids | workorders.return_move_ids
            )

    def action_view_subcontract_purchase_orders(self):
        self.ensure_one()
        purchase_orders = self.workorder_ids.purchase_order_line_ids.order_id
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        if len(purchase_orders) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "views": [
                        (self.env.ref("purchase.purchase_order_form").id, "form")
                    ],
                    "res_id": purchase_orders.id,
                }
            )
            action.pop("domain", None)
            return action
        action["views"] = [
            (
                self.env.ref(
                    "mrp_workorder_subcontracting."
                    "purchase_order_view_tree_subcontracting_documents"
                ).id,
                "list",
            ),
            (self.env.ref("purchase.purchase_order_form").id, "form"),
        ]
        action["domain"] = [("id", "in", purchase_orders.ids)]
        return action

    def action_view_subcontract_transfers(self):
        self.ensure_one()
        moves = (
            self.workorder_ids.delivery_move_ids | self.workorder_ids.return_move_ids
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Subcontract Transfers"),
            "res_model": "stock.move",
            "view_mode": "list,form",
            "views": [
                (
                    self.env.ref(
                        "mrp_workorder_subcontracting."
                        "stock_move_view_tree_subcontracting_transfers"
                    ).id,
                    "list",
                )
            ],
            "domain": [("id", "in", moves.ids)],
            "context": {
                "group_by": ["sub_workorder_id", "picking_type_id", "picking_id"],
                "expand": 1,
            },
        }

    def _link_subcontract_component_workorders(self):
        for production in self:
            workorders_by_operation = {
                workorder.operation_id.id: workorder
                for workorder in production.workorder_ids.filtered(
                    lambda workorder: (
                        workorder.operation_id and workorder.subcontract_ok
                    )
                )
            }
            moves_to_clear = self.env["stock.move"]
            moves_by_workorder = {}
            for move in production.move_raw_ids:
                workorder = self.env["mrp.workorder"]
                operation = move.bom_line_id.operation_id
                if operation:
                    workorder = workorders_by_operation.get(operation.id, workorder)
                if workorder:
                    if move.sub_component_workorder_id != workorder:
                        moves_by_workorder.setdefault(workorder, self.env["stock.move"])
                        moves_by_workorder[workorder] |= move
                elif move.sub_component_workorder_id and (
                    move.sub_component_workorder_id.production_id != production
                    or not move.sub_component_workorder_id.subcontract_ok
                ):
                    moves_to_clear |= move

            if moves_to_clear:
                moves_to_clear.write({"sub_component_workorder_id": False})
            for workorder, moves in moves_by_workorder.items():
                moves.write({"sub_component_workorder_id": workorder.id})
