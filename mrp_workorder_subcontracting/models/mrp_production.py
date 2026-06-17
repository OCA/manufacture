from odoo import _, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    subcontract_purchase_order_count = fields.Integer(
        string="Subcontract Purchase Orders",
        compute="_compute_subcontract_counts",
    )
    subcontract_transfer_count = fields.Integer(
        string="Subcontract Transfers",
        compute="_compute_subcontract_counts",
    )

    def _compute_subcontract_counts(self):
        for production in self:
            workorders = production.workorder_ids.filtered("subcontract_ok")
            production.subcontract_purchase_order_count = len(
                workorders.purchase_order_line_ids.order_id
            )
            production.subcontract_transfer_count = len(
                workorders.delivery_move_ids.picking_id
                | workorders.return_move_ids.picking_id
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
            },
        }
