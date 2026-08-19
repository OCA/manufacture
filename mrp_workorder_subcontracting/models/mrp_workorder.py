from markupsafe import Markup, escape

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    subcontract_ok = fields.Boolean(string="Subcontract", default=False)
    subcontract_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Subcontract Suppliers",
        copy=False,
    )
    subcontract_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Subcontract Service",
        domain=[("type", "=", "service"), ("purchase_ok", "=", True)],
        copy=False,
    )
    subcontract_flow_type = fields.Selection(
        selection=[
            ("standard", "Standard"),
            ("urgent", "Urgent"),
            ("subcontractor_stock", "Subcontractor stock"),
        ],
        copy=False,
        readonly=True,
    )
    subcontracting_flow = fields.Selection(
        [
            ("parts", "Sending Parts"),
            ("finished", "Sending Finished Product"),
        ],
        string="Subcontracting Supply Method",
        compute="_compute_subcontracting_flow",
    )
    purchase_order_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="workorder_id",
        string="Purchase Order Line",
        readonly=True,
    )
    delivery_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="sub_delivery_workorder_id",
        string="Delivery Moves",
        readonly=True,
    )
    return_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="sub_return_workorder_id",
        string="Return Moves",
        readonly=True,
    )
    sub_component_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="sub_component_workorder_id",
        string="Subcontract Component Moves",
        readonly=True,
    )
    has_subcontract_documents = fields.Boolean(
        compute="_compute_has_subcontract_documents",
    )
    subcontract_exception = fields.Boolean(
        copy=False,
        readonly=True,
    )
    subcontract_exception_message = fields.Text(
        copy=False,
        readonly=True,
    )
    subcontract_state = fields.Selection(
        selection=[
            ("none", "No Documents"),
            ("bidding", "Bid In Progress"),
            ("rfq", "RFQ Created"),
            ("confirmed", "Purchase Confirmed"),
            ("logistics", "Logistics In Progress"),
            ("done", "Completed"),
            ("exception", "Exception"),
        ],
        string="Subcontract Status",
        compute="_compute_subcontract_state",
    )

    @api.model_create_multi
    def create(self, vals_list):
        workorders = super().create(vals_list)
        workorders._sync_subcontracting_from_operation()
        return workorders

    def write(self, vals):
        res = super().write(vals)
        if "operation_id" in vals:
            self._sync_subcontracting_from_operation()
        return res

    def button_create_subcontract_order(self):
        self.ensure_one()
        action = self.env.ref(
            "mrp_workorder_subcontracting.mrp_workorder_assign_subcontract_action"
        ).read()[0]
        action["context"] = {
            **self.env.context,
            "default_workorder_ids": self.ids,
            "active_ids": self.ids,
            "active_id": self.id,
            "active_model": self._name,
        }

        return action

    def action_view_subcontract_purchase_orders(self):
        self.ensure_one()
        purchase_orders = self.purchase_order_line_ids.order_id
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
        moves = self.delivery_move_ids | self.return_move_ids
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

    def _action_confirm(self):
        res = super()._action_confirm()
        self._sync_subcontracting_from_operation()
        self.mapped("production_id")._link_subcontract_component_workorders()
        return res

    def _sync_subcontracting_from_operation(self):
        for workorder in self.filtered("operation_id"):
            if workorder.has_subcontract_documents:
                continue
            operation = workorder.operation_id
            workorder.write(
                {
                    "subcontract_ok": operation.subcontract_ok,
                    "subcontract_partner_ids": [
                        (6, 0, operation.subcontractor_partner_ids.ids)
                    ],
                    "subcontract_product_id": operation.subcontract_product_id.id,
                }
            )

    @api.constrains("delivery_move_ids", "return_move_ids")
    def _check_subcontract_supplier_consistency(self):
        for workorder in self.filtered("subcontract_ok"):
            partners = workorder.delivery_move_ids.filtered(
                lambda move: move.state != "cancel"
            ).mapped("partner_id") | workorder.return_move_ids.filtered(
                lambda move: move.state != "cancel"
            ).mapped("partner_id")
            if len(partners) > 1:
                raise ValidationError(
                    _(
                        "Subcontract logistics for workorder '%s' must be linked "
                        "to a single supplier."
                    )
                    % workorder.display_name
                )

    @api.depends("sub_component_move_ids")
    def _compute_subcontracting_flow(self):
        for workorder in self:
            workorder.subcontracting_flow = (
                "parts" if workorder.sub_component_move_ids else "finished"
            )

    @api.depends("purchase_order_line_ids", "delivery_move_ids", "return_move_ids")
    def _compute_has_subcontract_documents(self):
        for workorder in self:
            workorder.has_subcontract_documents = bool(
                workorder.purchase_order_line_ids
                or workorder.delivery_move_ids
                or workorder.return_move_ids
            )

    @api.depends(
        "subcontract_ok",
        "subcontract_exception",
        "purchase_order_line_ids.state",
        "purchase_order_line_ids.subcontract_lost_bid",
        "delivery_move_ids.state",
        "return_move_ids.state",
        "state",
    )
    def _compute_subcontract_state(self):
        for workorder in self:
            if not workorder.subcontract_ok:
                workorder.subcontract_state = False
                continue
            if workorder.subcontract_exception:
                workorder.subcontract_state = "exception"
                continue
            active_po_lines = workorder.purchase_order_line_ids.filtered(
                lambda line: not line.subcontract_lost_bid
            )
            open_po_lines = active_po_lines.filtered(
                lambda line: line.state in ("draft", "sent", "to_approve")
            )
            confirmed_po_lines = active_po_lines.filtered(
                lambda line: line.state in ("purchase", "done")
            )
            open_delivery = workorder.delivery_move_ids.filtered(
                lambda move: move.state not in ("done", "cancel")
            )
            open_return = workorder.return_move_ids.filtered(
                lambda move: move.state not in ("done", "cancel")
            )
            done_return = workorder.return_move_ids.filtered(
                lambda move: move.state == "done"
            )
            if workorder.state == "done" or done_return:
                workorder.subcontract_state = "done"
            elif (
                open_delivery
                or open_return
                or workorder.delivery_move_ids
                or workorder.return_move_ids
            ):
                workorder.subcontract_state = "logistics"
            elif confirmed_po_lines:
                workorder.subcontract_state = "confirmed"
            elif len(open_po_lines.mapped("order_id.partner_id")) > 1:
                workorder.subcontract_state = "bidding"
            elif open_po_lines:
                workorder.subcontract_state = "rfq"
            else:
                workorder.subcontract_state = "none"

    def _post_subcontract_message(self, title, details=None):
        details = details or []
        for production in self.mapped("production_id"):
            related_workorders = self.filtered(
                lambda wo, production=production: wo.production_id == production
            )
            body_lines = [Markup("<p><b>%s</b></p>") % escape(title)]
            if details:
                body_lines.append(
                    Markup("<p>%s</p>") % escape("; ".join(filter(None, details)))
                )
            body_lines.append(
                Markup("<p>%s</p>")
                % escape(
                    _("Workorders: %s")
                    % ", ".join(related_workorders.mapped("display_name"))
                )
            )
            production.message_post(
                body=Markup("").join(body_lines),
                subtype_xmlid="mail.mt_note",
            )

    def _evaluate_subcontract_execution(self):
        for workorder in self.filtered(
            lambda wo: wo.subcontract_ok and wo.state not in ("done", "cancel")
        ):
            open_delivery = workorder.delivery_move_ids.filtered(
                lambda move: move.state not in ("done", "cancel")
            )
            open_return = workorder.return_move_ids.filtered(
                lambda move: move.state not in ("done", "cancel")
            )
            if open_delivery or open_return:
                if (
                    workorder.subcontract_exception
                    or workorder.subcontract_exception_message
                ):
                    workorder.write(
                        {
                            "subcontract_exception": False,
                            "subcontract_exception_message": False,
                        }
                    )
                continue

            done_return_moves = workorder.return_move_ids.filtered(
                lambda move: move.state == "done"
            )
            received_qty = sum(
                move.product_uom._compute_quantity(
                    move.quantity,
                    workorder.product_uom_id,
                    rounding_method="HALF-UP",
                )
                for move in done_return_moves
            )
            if not float_is_zero(
                received_qty, precision_rounding=workorder.product_uom_id.rounding
            ):
                workorder.write(
                    {
                        "subcontract_exception": False,
                        "subcontract_exception_message": False,
                    }
                )
                qty_to_finish = min(workorder.qty_remaining, received_qty)
                if (
                    float_compare(
                        qty_to_finish,
                        0.0,
                        precision_rounding=workorder.product_uom_id.rounding,
                    )
                    > 0
                ):
                    workorder.qty_producing = qty_to_finish
                    workorder.button_finish()
            else:
                message = _(
                    "No subcontract receipt has been completed. Check cancelled "
                    "or missing receipt documents."
                )
                cancelled_moves = (
                    workorder.delivery_move_ids | workorder.return_move_ids
                ).filtered(lambda move: move.state == "cancel")
                if cancelled_moves and not workorder.subcontract_exception:
                    workorder._post_subcontract_message(
                        _("Subcontract exception"),
                        [message],
                    )
                workorder.write(
                    {
                        "subcontract_exception": True,
                        "subcontract_exception_message": message,
                    }
                )

    def _get_subcontract_return_qty(self, states=None, use_done_qty=False):
        self.ensure_one()
        moves = self.return_move_ids
        if states:
            moves = moves.filtered(lambda move: move.state in states)
        total = 0.0
        for move in moves:
            qty = (
                move.quantity
                if use_done_qty and move.state == "done"
                else move.product_uom_qty
            )
            total += move.product_uom._compute_quantity(
                qty,
                self.product_uom_id,
                rounding_method="HALF-UP",
            )
        return total

    def _get_subcontract_delivery_done_qty(self):
        self.ensure_one()
        total = 0.0
        for move in self.delivery_move_ids.filtered(lambda move: move.state == "done"):
            total += move.product_uom._compute_quantity(
                move.quantity,
                self.product_uom_id,
                rounding_method="HALF-UP",
            )
        return total

    def _get_subcontract_target_return_qty(self):
        self.ensure_one()
        if self.subcontracting_flow == "finished":
            return self._get_subcontract_delivery_done_qty()

        delivery_moves = self.delivery_move_ids.filtered(
            lambda move: move.state != "cancel"
        )
        return self._get_subcontract_target_qty_from_delivery_moves(
            delivery_moves, self.qty_remaining
        )

    def _get_subcontract_target_qty_from_delivery_moves(self, delivery_moves, qty):
        self.ensure_one()
        ratios = []
        for product in delivery_moves.mapped("product_id"):
            product_moves = delivery_moves.filtered(
                lambda move, p=product: move.product_id == p
            )
            target_uom = min(
                product_moves.mapped("product_uom"), key=lambda uom: uom.rounding
            )  # Take smaller UoM
            planned_qty = sum(
                move.product_uom._compute_quantity(
                    move.product_uom_qty,
                    target_uom,
                    rounding_method="HALF-UP",
                )
                for move in product_moves
            )  # Convert and sum to reference UoM
            done_qty = sum(
                move.product_uom._compute_quantity(
                    move.quantity if move.state == "done" else 0.0,
                    target_uom,
                    rounding_method="HALF-UP",
                )
                for move in product_moves
            )  # Convert and sum to reference UoM
            if not planned_qty:
                continue
            ratios.append(done_qty / planned_qty)
        if not ratios:
            return 0.0
        return float_round(
            qty * min(ratios),
            precision_rounding=self.product_uom_id.rounding,
        )

    def _sync_subcontract_raw_move_location(self, partner=False):
        internal_location = (
            partner.property_stock_subcontract_location_id if partner else False
        ) or self.env.ref(
            "mrp_workorder_subcontracting.stock_location_subcontractors_general",
            raise_if_not_found=False,
        )
        if not internal_location:
            return
        raw_moves = self._get_subcontract_component_moves().filtered(
            lambda move: move.state not in ("done", "cancel")
        )
        raw_moves.write({"location_id": internal_location.id})

    def _get_subcontract_component_moves(self):
        return self.sub_component_move_ids
