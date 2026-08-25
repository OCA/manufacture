from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    _LOST_BID_PROTECTED_FIELDS = {
        "product_id",
        "product_qty",
        "product_uom",
        "price_unit",
        "date_planned",
        "name",
        "taxes_id",
    }

    workorder_id = fields.Many2one(
        comodel_name="mrp.workorder", string="Work Order", index=True
    )
    production_id = fields.Many2one(
        related="workorder_id.production_id", string="Manufacturing Order"
    )
    subcontracting_flow = fields.Selection(
        related="workorder_id.subcontracting_flow",
        string="Subcontracting Supply Method",
        store=True,
        readonly=True,
    )
    subcontract_lost_bid = fields.Boolean(
        string="Lost Bid",
        copy=False,
        readonly=True,
    )
    sub_purchase_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="sub_purchase_line_id",
        string="Subcontract Delivery Moves",
        readonly=True,
        domain=[("sub_delivery_workorder_id", "!=", False)],
    )
    subcontract_receipt_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="sub_purchase_line_id",
        string="Subcontract Receipt Moves",
        readonly=True,
        domain=[("sub_return_workorder_id", "!=", False)],
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._check_subcontract_partner_consistency()
        lines._sync_existing_subcontract_documents()
        return lines

    def _get_subcontract_receipt_qty(self, states=None, use_done_qty=False):
        self.ensure_one()
        moves = self.subcontract_receipt_move_ids.filtered("sub_return_workorder_id")
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
                self.workorder_id.product_uom_id,
                rounding_method="HALF-UP",
            )
        return total

    def _get_subcontract_delivery_done_qty(self):
        self.ensure_one()
        total = 0.0
        for move in self.sub_purchase_move_ids.filtered(
            lambda move: move.sub_delivery_workorder_id and move.state == "done"
        ):
            total += move.product_uom._compute_quantity(
                move.quantity,
                self.workorder_id.product_uom_id,
                rounding_method="HALF-UP",
            )
        return total

    def _get_subcontract_target_receipt_qty(self):
        self.ensure_one()
        if self.subcontracting_flow == "finished":
            return self._get_subcontract_delivery_done_qty()

        delivery_moves = self.sub_purchase_move_ids.filtered(
            lambda move: move.sub_delivery_workorder_id and move.state != "cancel"
        )
        return self.workorder_id._get_subcontract_target_qty_from_delivery_moves(
            delivery_moves, self.product_qty
        )

    def write(self, vals):
        old_workorders_by_line = [
            (line, line.workorder_id)
            for line in self
            if "workorder_id" in vals and line.workorder_id
        ]
        if not self.env.context.get(
            "allow_lost_bid_write"
        ) and self._LOST_BID_PROTECTED_FIELDS.intersection(vals):
            blocked_lines = self.filtered("subcontract_lost_bid")
            if blocked_lines:
                raise ValidationError(
                    _(
                        "You cannot modify a purchase order line that lost "
                        "the subcontracting bid."
                    )
                )
        res = super().write(vals)
        if {"workorder_id", "order_id"}.intersection(vals):
            self._check_subcontract_partner_consistency()
        if old_workorders_by_line:
            for line, old_workorder in old_workorders_by_line:
                if line.workorder_id != old_workorder:
                    line._unlink_old_subcontract_documents(old_workorder)
        if {"workorder_id", "order_id", "product_id"}.intersection(vals):
            self._sync_existing_subcontract_documents()
        return res

    def _check_subcontract_partner_consistency(self):
        for line in self.filtered("workorder_id"):
            partner = line.order_id.partner_id
            workorder_partners = line.workorder_id.subcontract_partner_ids
            if workorder_partners and partner not in workorder_partners:
                raise ValidationError(
                    _(
                        "Purchase order supplier '%(supplier)s' is not allowed "
                        "for work order '%(workorder)s'."
                    )
                    % {
                        "supplier": partner.display_name,
                        "workorder": line.workorder_id.display_name,
                    }
                )
            move_partners = (
                (
                    line.workorder_id.delivery_move_ids
                    | line.workorder_id.return_move_ids
                )
                .filtered(lambda move: move.state != "cancel")
                .mapped("picking_id.partner_id")
            )
            if move_partners and partner not in move_partners:
                raise ValidationError(
                    _(
                        "Purchase order supplier '%(supplier)s' does not match "
                        "the supplier already used by the subcontracting "
                        "transfers for work order '%(workorder)s'."
                    )
                    % {
                        "supplier": partner.display_name,
                        "workorder": line.workorder_id.display_name,
                    }
                )

    def _unlink_old_subcontract_documents(self, old_workorder):
        self.ensure_one()
        moves = (
            old_workorder.delivery_move_ids | old_workorder.return_move_ids
        ).filtered(lambda move: move.sub_purchase_line_id == self)
        moves.write({"sub_purchase_line_id": False})

    def _sync_existing_subcontract_documents(self):
        for line in self.filtered("workorder_id"):
            line._sync_workorder_subcontract_reference()
            moves = (
                line.workorder_id.delivery_move_ids | line.workorder_id.return_move_ids
            ).filtered(
                lambda move: not move.sub_purchase_line_id and move.state != "cancel"
            )
            if moves:
                moves.write({"sub_purchase_line_id": line.id})

    def _sync_workorder_subcontract_reference(self):
        self.ensure_one()
        vals = {}
        if self.order_id.partner_id:
            partner_ids = (
                self.workorder_id.subcontract_partner_ids | self.order_id.partner_id
            ).ids
            vals["subcontract_partner_ids"] = [(6, 0, partner_ids)]
        if self.product_id and self.product_id.type == "service":
            vals["subcontract_product_id"] = self.product_id.id
        if vals:
            self.workorder_id.write(vals)
