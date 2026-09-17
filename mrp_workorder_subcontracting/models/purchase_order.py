from markupsafe import Markup, escape

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_subcontracting = fields.Boolean(
        string="Subcontracting",
        related="order_type.is_subcontracting",
    )
    subcontract_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Subcontract Location",
        index=True,
    )
    mrp_subcontracting = fields.Boolean(
        string="Mrp subcontracting",
        compute="_compute_mrp_subcontracting",
    )
    has_mixed_subcontract_flows = fields.Boolean(
        compute="_compute_has_mixed_subcontract_flows",
    )
    subcontract_workorder_count = fields.Integer(
        string="Subcontract Work Orders",
        compute="_compute_subcontract_counts",
    )
    subcontract_transfer_count = fields.Integer(
        string="Subcontract Transfers Count", compute="_compute_subcontract_counts"
    )

    def _compute_mrp_subcontracting(self):
        for po in self:
            if po.mapped("order_line").mapped("workorder_id"):
                po.mrp_subcontracting = True
            else:
                po.mrp_subcontracting = False

    def _compute_has_mixed_subcontract_flows(self):
        for po in self:
            flows = set(po.order_line.mapped("subcontracting_flow"))
            po.has_mixed_subcontract_flows = len(flows - {False}) > 1

    def _compute_subcontract_counts(self):
        for po in self:
            workorders = po.order_line.mapped("workorder_id")
            po.subcontract_workorder_count = len(workorders)
            pickings = (
                workorders.delivery_move_ids.picking_id
                | workorders.return_move_ids.picking_id
            )
            po.subcontract_transfer_count = len(pickings)

    def action_view_subcontract_workorders(self):
        self.ensure_one()
        workorders = self.order_line.mapped("workorder_id")
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

    def action_view_subcontract_transfers(self):
        self.ensure_one()
        workorders = self.order_line.mapped("workorder_id")
        moves = workorders.delivery_move_ids | workorders.return_move_ids
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

    def button_confirm(self):
        competitor_lines_by_order = {}
        for order in self.filtered("mrp_subcontracting"):
            order._check_subcontract_bid_confirm_conflicts()
            competitor_lines = order._get_open_subcontract_bid_competitor_lines()
            if competitor_lines:
                competitor_lines_by_order[order.id] = competitor_lines
                if not self.env.context.get("skip_subcontract_bid_wizard"):
                    return order._open_subcontract_bid_confirm_wizard(competitor_lines)
        res = super().button_confirm()
        for order in self.filtered("mrp_subcontracting"):
            competitor_lines = competitor_lines_by_order.get(
                order.id, self.env["purchase.order.line"]
            )
            order._resolve_subcontract_bid_competitors(competitor_lines)
            order._apply_subcontract_bid_winner(competitor_lines)
            order._ensure_subcontract_pickings()
        return res

    def _get_subcontract_bid_workorders(self):
        self.ensure_one()
        return self.order_line.filtered(
            lambda line: line.workorder_id and not line.subcontract_lost_bid
        ).mapped("workorder_id")

    def _get_open_subcontract_bid_competitor_lines(self):
        self.ensure_one()
        workorders = self._get_subcontract_bid_workorders()
        if not workorders:
            return self.env["purchase.order.line"]
        return self.env["purchase.order.line"].search(
            [
                ("workorder_id", "in", workorders.ids),
                ("subcontract_lost_bid", "=", False),
                ("order_id", "!=", self.id),
                ("order_id.partner_id", "!=", self.partner_id.id),
                ("order_id.state", "in", ["draft", "sent", "to_approve"]),
            ]
        )

    def _check_subcontract_bid_confirm_conflicts(self):
        self.ensure_one()
        workorders = self._get_subcontract_bid_workorders()
        if not workorders:
            return
        confirmed_lines = self.env["purchase.order.line"].search(
            [
                ("workorder_id", "in", workorders.ids),
                ("subcontract_lost_bid", "=", False),
                ("order_id", "!=", self.id),
                ("order_id.state", "in", ["purchase", "done"]),
            ],
            limit=1,
        )
        if confirmed_lines:
            raise ValidationError(
                _(
                    "Another subcontracting purchase order has already won "
                    "the bid for workorder '%s'."
                )
                % confirmed_lines.workorder_id.display_name
            )

    def _open_subcontract_bid_confirm_wizard(self, competitor_lines):
        self.ensure_one()
        wizard = self.env["purchase.order.subcontract.bid.wizard"].create(
            {
                "purchase_order_id": self.id,
                "competitor_order_ids": [(6, 0, competitor_lines.order_id.ids)],
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Confirm Winning Bid"),
            "res_model": "purchase.order.subcontract.bid.wizard",
            "view_mode": "form",
            "target": "new",
            "res_id": wizard.id,
        }

    def _resolve_subcontract_bid_competitors(self, competitor_lines=None):
        self.ensure_one()
        if competitor_lines is None:
            competitor_lines = self._get_open_subcontract_bid_competitor_lines()
        for competitor_order in competitor_lines.order_id:
            lost_lines = competitor_lines.filtered(
                lambda line, competitor_order=competitor_order: (
                    line.order_id == competitor_order
                )
            )
            active_lines = competitor_order.order_line.filtered(
                lambda line: not line.display_type and not line.subcontract_lost_bid
            )
            if active_lines and set(active_lines.ids) == set(lost_lines.ids):
                body = Markup("<p>%s</p>") % (
                    _(
                        "This subcontracting request for quotation lost the bid "
                        "against purchase order %(order)s.",
                        order=self._get_html_link(),
                    )
                )
                competitor_order.message_post(
                    body=body,
                    subtype_xmlid="mail.mt_note",
                )
                competitor_order.button_cancel()
                continue
            lost_lines.with_context(allow_lost_bid_write=True).write(
                {
                    "product_qty": 0.0,
                    "subcontract_lost_bid": True,
                }
            )
            competitor_order._message_subcontract_bid_lost(lost_lines, self)

    def _apply_subcontract_bid_winner(self, competitor_lines=None):
        self.ensure_one()
        winner_workorders = self.env["mrp.workorder"]
        for line in self.order_line.filtered(
            lambda po_line: po_line.workorder_id and not po_line.subcontract_lost_bid
        ):
            vals = {
                "subcontract_partner_ids": [(6, 0, self.partner_id.ids)],
                "subcontract_product_id": line.product_id.id,
            }
            line.workorder_id.write(vals)
            winner_workorders |= line.workorder_id
        if winner_workorders and competitor_lines:
            winner_workorders._post_subcontract_message(
                _("Subcontract bid confirmed"),
                [
                    _("Winning purchase order: %s") % self.display_name,
                    _("Supplier: %s") % self.partner_id.display_name,
                    _("Discarded purchase orders: %s")
                    % ", ".join(competitor_lines.order_id.mapped("display_name")),
                ],
            )

    def _message_subcontract_bid_lost(self, lost_lines, winner_order):
        self.ensure_one()
        line_items = Markup().join(
            Markup("<li>%s</li>")
            % escape(f"{line.name} ({line.workorder_id.display_name})")
            for line in lost_lines
        )
        body = Markup("<p>%s</p><ul>%s</ul>") % (
            _(
                "Some subcontracting lines lost the bid against purchase order "
                "%(order)s.",
                order=winner_order._get_html_link(),
            ),
            line_items,
        )
        self.message_post(body=body, subtype_xmlid="mail.mt_note")

    def _ensure_subcontract_pickings(self):
        for order in self:
            outgoing_lines = order.order_line.filtered(
                lambda line: line.workorder_id
                and line.workorder_id.subcontract_flow_type == "standard"
            )
            if outgoing_lines:
                outgoing_lines.mapped("workorder_id").filtered(
                    lambda workorder: workorder.subcontracting_flow == "parts"
                )._sync_subcontract_raw_move_location(order.partner_id)
                order._ensure_outgoing_pickings(outgoing_lines)
                if order.order_type.immediate_return_subcontracting:
                    order._ensure_immediate_incoming_pickings(outgoing_lines)

    def _ensure_outgoing_pickings(self, lines):
        for flow_type in ("parts", "finished"):
            flow_lines = lines.filtered(
                lambda line, flow_type=flow_type: (
                    line.subcontracting_flow == flow_type
                )
            )
            if not flow_lines:
                continue
            picking = self._get_or_create_subcontract_picking("out", flow_type)
            move_values = []
            for line in flow_lines:
                if line.sub_purchase_move_ids.filtered(
                    lambda move: move.sub_delivery_workorder_id
                    and move.state != "cancel"
                ):
                    continue
                move_values += self._prepare_outgoing_move_vals(line, picking)
            if move_values:
                created_moves = self.env["stock.move"].create(move_values)
                created_moves._action_confirm(merge=False)
                if picking.picking_type_id.reservation_method == "at_confirm":
                    picking.action_assign()

    def _ensure_immediate_incoming_pickings(self, lines):
        for flow_type in ("parts", "finished"):
            flow_lines = lines.filtered(
                lambda line, flow_type=flow_type: (
                    line.subcontracting_flow == flow_type
                )
            )
            if not flow_lines:
                continue
            picking = self._get_or_create_subcontract_picking("in", flow_type)
            move_values = []
            for line in flow_lines:
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
                if (
                    float_compare(
                        existing_qty,
                        line.product_qty,
                        precision_rounding=line.workorder_id.product_uom_id.rounding,
                    )
                    >= 0
                ):
                    continue
                move_values.append(
                    self._prepare_incoming_finished_move_vals(
                        line, picking, line.product_qty - existing_qty
                    )
                )
            if move_values:
                created_moves = self.env["stock.move"].create(move_values)
                created_moves._action_confirm(merge=False)
                if picking.picking_type_id.reservation_method == "at_confirm":
                    picking.action_assign()

    def _get_or_create_subcontract_picking(self, direction, flow_type):
        self.ensure_one()
        if direction == "out":
            picking_type = (
                self.order_type.sub_out_picking_type_id
                if flow_type == "parts"
                else self.order_type.sub_out_virtual_picking_type_id
            )
        else:
            picking_type = (
                self.order_type.sub_in_picking_type_id
                if flow_type == "parts"
                else self.order_type.sub_in_virtual_picking_type_id
            )
        if not picking_type:
            raise ValidationError(
                _(
                    "Missing subcontract picking type configuration for flow "
                    "'%(flow)s' on purchase order type '%(type)s'."
                )
                % {"flow": flow_type, "type": self.order_type.display_name}
            )
        if direction == "out":
            partner_location = (
                self.partner_id.property_stock_subcontract_location_id
                if flow_type == "parts"
                else self.partner_id.property_stock_virtual_subcontract_location_id
            )
            location_id = picking_type.default_location_src_id
            location_dest_id = partner_location or picking_type.default_location_dest_id
        else:
            location_id = (
                self.partner_id.property_stock_virtual_subcontract_location_id
                if flow_type == "finished"
                else picking_type.default_location_src_id
            ) or picking_type.default_location_src_id
            location_dest_id = picking_type.default_location_dest_id
        if not location_id or not location_dest_id:
            raise ValidationError(
                _(
                    "Missing subcontract locations for purchase order "
                    "'%(order)s' and flow '%(flow)s'."
                )
                % {"order": self.display_name, "flow": flow_type}
            )
        picking = self.env["stock.picking"].search(
            [
                ("partner_id", "=", self.partner_id.id),
                ("picking_type_id", "=", picking_type.id),
                ("location_id", "=", location_id.id),
                ("location_dest_id", "=", location_dest_id.id),
                ("state", "not in", ["done", "cancel"]),
            ],
            limit=1,
            order="id desc",
        )
        if picking:
            return picking
        return self.env["stock.picking"].create(
            {
                "partner_id": self.partner_id.id,
                "picking_type_id": picking_type.id,
                "location_id": location_id.id,
                "location_dest_id": location_dest_id.id,
                "origin": self.name,
                "scheduled_date": self.date_planned,
            }
        )

    def _prepare_outgoing_move_vals(self, line, picking):
        if line.subcontracting_flow == "finished":
            return [
                {
                    "name": line.workorder_id.product_id.display_name,
                    "product_id": line.workorder_id.product_id.id,
                    "product_uom": line.workorder_id.product_uom_id.id,
                    "product_uom_qty": line.product_qty,
                    "location_id": picking.location_id.id,
                    "location_dest_id": picking.location_dest_id.id,
                    "picking_id": picking.id,
                    "origin": self.name,
                    "company_id": picking.company_id.id,
                    "warehouse_id": picking.picking_type_id.warehouse_id.id,
                    "sub_purchase_line_id": line.id,
                    "sub_delivery_workorder_id": line.workorder_id.id,
                }
            ]

        factor = (
            line.product_qty / line.workorder_id.qty_remaining
            if line.workorder_id.qty_remaining
            else 0.0
        )
        values = []
        for raw_move in line.workorder_id._get_subcontract_component_moves().filtered(
            lambda move: move.state not in ("done", "cancel")
        ):
            values.append(
                {
                    "name": raw_move.display_name or raw_move.product_id.display_name,
                    "product_id": raw_move.product_id.id,
                    "product_uom": raw_move.product_uom.id,
                    "product_uom_qty": raw_move.product_uom_qty * factor,
                    "location_id": picking.location_id.id,
                    "location_dest_id": picking.location_dest_id.id,
                    "picking_id": picking.id,
                    "origin": self.name,
                    "company_id": picking.company_id.id,
                    "warehouse_id": picking.picking_type_id.warehouse_id.id,
                    "sub_purchase_line_id": line.id,
                    "sub_delivery_workorder_id": line.workorder_id.id,
                }
            )
        return values

    def _prepare_incoming_finished_move_vals(self, line, picking, qty):
        return {
            "name": line.workorder_id.product_id.display_name,
            "product_id": line.workorder_id.product_id.id,
            "product_uom": line.workorder_id.product_uom_id.id,
            "product_uom_qty": qty,
            "location_id": picking.location_id.id,
            "location_dest_id": picking.location_dest_id.id,
            "picking_id": picking.id,
            "origin": self.name,
            "company_id": picking.company_id.id,
            "warehouse_id": picking.picking_type_id.warehouse_id.id,
            "sub_purchase_line_id": line.id,
            "sub_return_workorder_id": line.workorder_id.id,
        }
