from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_subcontract_pick_type = fields.Boolean(related="picking_type_id.is_subcontract")
    subcontract_parts = fields.Boolean(
        string="Is subcontract parts?", compute="_compute_subcontract_flags"
    )
    sub_workorder_count = fields.Integer(
        string="Number of Subcontract Work Orders",
        compute="_compute_sub_workorder_count",
    )

    @api.depends("move_ids.sub_workorder_id")
    def _compute_sub_workorder_count(self):
        for picking in self:
            picking.sub_workorder_count = len(
                picking.move_ids.mapped("sub_workorder_id")
            )

    @api.depends("location_id", "location_dest_id")
    def _compute_subcontract_flags(self):
        for picking in self:
            if not picking.is_subcontract_pick_type:
                picking.subcontract_parts = False
                continue
            picking.subcontract_parts = not (
                picking.location_id.usage == "production"
                and picking.location_dest_id.usage == "production"
            )

    def _action_done(self):
        res = super()._action_done()
        self._sync_subcontract_incoming_from_done_outgoing()
        self._evaluate_subcontract_workorders()
        return res

    def action_cancel(self):
        res = super().action_cancel()
        self._evaluate_subcontract_workorders()
        return res

    def _sync_subcontract_incoming_from_done_outgoing(self):
        outgoing_pickings = self.filtered(
            lambda picking: picking.state == "done"
            and picking.picking_type_code == "outgoing"
            and picking.move_ids.filtered("sub_delivery_workorder_id")
        )
        for picking in outgoing_pickings:
            impacted_lines = picking.move_ids.mapped("sub_purchase_line_id")
            for line in impacted_lines:
                order = line.order_id
                if order.order_type.immediate_return_subcontracting:
                    continue
                target_qty = line._get_subcontract_target_receipt_qty()
                existing_qty = line._get_subcontract_receipt_qty(
                    states=[
                        "draft",
                        "waiting",
                        "confirmed",
                        "assigned",
                        "partially_available",
                        "done",
                    ]
                )
                rounding = line.workorder_id.product_uom_id.rounding
                if (
                    float_compare(target_qty, existing_qty, precision_rounding=rounding)
                    <= 0
                ):
                    continue
                return_move = picking._get_open_subcontract_return_move(
                    line.workorder_id, purchase_line=line
                )
                if return_move:
                    picking._update_subcontract_return_move(
                        return_move, line.workorder_id, target_qty - existing_qty
                    )
                    in_picking = return_move.picking_id
                else:
                    flow_type = line.subcontracting_flow
                    in_picking = order._get_or_create_subcontract_picking(
                        "in", flow_type
                    )
                    picking._create_subcontract_return_move(
                        order._prepare_incoming_finished_move_vals(
                            line,
                            in_picking,
                            target_qty - existing_qty,
                        )
                    )
                if in_picking.picking_type_id.reservation_method == "at_confirm":
                    in_picking.action_assign()

            no_purchase_moves = picking.move_ids.filtered(
                lambda move: move.sub_delivery_workorder_id
                and not move.sub_purchase_line_id
            )
            for workorder in no_purchase_moves.mapped("sub_delivery_workorder_id"):
                target_qty = workorder._get_subcontract_target_return_qty()
                existing_qty = workorder._get_subcontract_return_qty(
                    states=[
                        "draft",
                        "waiting",
                        "confirmed",
                        "assigned",
                        "partially_available",
                        "done",
                    ]
                )
                rounding = workorder.product_uom_id.rounding
                if (
                    float_compare(target_qty, existing_qty, precision_rounding=rounding)
                    <= 0
                ):
                    continue
                return_move = picking._get_open_subcontract_return_move(workorder)
                if return_move:
                    picking._update_subcontract_return_move(
                        return_move, workorder, target_qty - existing_qty
                    )
                    in_picking = return_move.picking_id
                else:
                    in_picking = picking._get_or_create_workorder_incoming_picking(
                        workorder
                    )
                    picking._create_subcontract_return_move(
                        picking._prepare_workorder_incoming_move_vals(
                            workorder, in_picking, target_qty - existing_qty
                        )
                    )
                if in_picking.picking_type_id.reservation_method == "at_confirm":
                    in_picking.action_assign()

    def _get_open_subcontract_return_move(
        self, workorder, picking=False, purchase_line=False
    ):
        self.ensure_one()
        moves = workorder.return_move_ids.filtered(
            lambda move: (
                move.state not in ("done", "cancel")
                and move.product_id == workorder.product_id
                and move.product_uom == workorder.product_uom_id
            )
        )
        if picking:
            moves = moves.filtered(lambda move: move.picking_id == picking)
        if purchase_line:
            moves = moves.filtered(
                lambda move: move.sub_purchase_line_id == purchase_line
            )
        else:
            moves = moves.filtered(lambda move: not move.sub_purchase_line_id)
        return moves[:1]

    def _update_subcontract_return_move(self, return_move, workorder, qty):
        return_qty = workorder.product_uom_id._compute_quantity(
            qty,
            return_move.product_uom,
            rounding_method="HALF-UP",
        )
        return_move.product_uom_qty += return_qty

    def _create_subcontract_return_move(self, move_vals):
        return_move = self.env["stock.move"].create(move_vals)
        return_move._action_confirm(merge=False)
        return return_move

    def _get_or_create_workorder_incoming_picking(self, workorder):
        self.ensure_one()
        warehouse = workorder.production_id.picking_type_id.warehouse_id
        picking_type = (
            warehouse.sub_in_picking_type_id
            if workorder.subcontracting_flow == "parts"
            else warehouse.sub_in_virtual_picking_type_id
        )
        if not picking_type:
            raise ValidationError(
                _(
                    "Missing subcontract incoming picking type for warehouse "
                    "'%(warehouse)s' and workorder '%(workorder)s'."
                )
                % {
                    "warehouse": warehouse.display_name,
                    "workorder": workorder.display_name,
                }
            )
        if workorder.subcontracting_flow == "parts":
            location_id = picking_type.default_location_src_id
        else:
            location_id = (
                self.partner_id.property_stock_virtual_subcontract_location_id
                or picking_type.default_location_src_id
            )
        open_picking = self.env["stock.picking"].search(
            [
                ("partner_id", "=", self.partner_id.id),
                ("picking_type_id", "=", picking_type.id),
                ("location_id", "=", location_id.id),
                ("location_dest_id", "=", picking_type.default_location_dest_id.id),
                ("state", "not in", ["done", "cancel"]),
            ],
            limit=1,
            order="id desc",
        )
        if open_picking:
            return open_picking
        return self.env["stock.picking"].create(
            {
                "partner_id": self.partner_id.id,
                "picking_type_id": picking_type.id,
                "location_id": location_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "origin": self.origin or workorder.production_id.display_name,
                "scheduled_date": self.scheduled_date,
            }
        )

    def _prepare_workorder_incoming_move_vals(self, workorder, picking, qty):
        return {
            "name": workorder.product_id.display_name,
            "product_id": workorder.product_id.id,
            "product_uom": workorder.product_uom_id.id,
            "product_uom_qty": qty,
            "location_id": picking.location_id.id,
            "location_dest_id": picking.location_dest_id.id,
            "picking_id": picking.id,
            "origin": self.origin or workorder.production_id.display_name,
            "company_id": picking.company_id.id,
            "warehouse_id": picking.picking_type_id.warehouse_id.id,
            "sub_return_workorder_id": workorder.id,
        }

    def _evaluate_subcontract_workorders(self):
        workorders = self.move_ids.mapped(
            "sub_delivery_workorder_id"
        ) | self.move_ids.mapped("sub_return_workorder_id")
        workorders._evaluate_subcontract_execution()

    def action_view_subcontract_workorders(self):
        self.ensure_one()
        workorders = self.move_ids.mapped("sub_workorder_id")
        return {
            "type": "ir.actions.act_window",
            "name": _("Subcontract Workorders"),
            "res_model": "mrp.workorder",
            "view_mode": "list,form",
            "views": [
                (
                    self.env.ref(
                        "mrp_workorder_subcontracting."
                        "mrp_workorder_view_tree_subcontracting_documents"
                    ).id,
                    "list",
                ),
                (False, "form"),
            ],
            "domain": [("id", "in", workorders.ids)],
        }
