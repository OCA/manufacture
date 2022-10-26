# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import SUPERUSER_ID, _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    subcontracting_resupply_count = fields.Integer(
        compute="_compute_subcontracting_resupply_ids",
        string="Resupply count",
        store=True,
    )
    subcontracting_resupply_ids = fields.Many2many(
        relation="stock_picking_resupply",
        column1="purchase_id",
        column2="picking_id",
        comodel_name="stock.picking",
        compute="_compute_subcontracting_resupply_ids",
        string="Resupplys",
        copy=False,
        store=True,
    )

    @api.depends("picking_ids")
    def _compute_subcontracting_resupply_ids(self):
        for order in self:
            pickings = False
            order_pickings = order.picking_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            )
            moves = order_pickings.move_lines.filtered(
                lambda x: x.is_subcontract and x.move_orig_ids
            )
            if moves:
                pickings = moves.mapped("move_orig_ids.production_id.picking_ids")
            order.subcontracting_resupply_ids = pickings
            order.subcontracting_resupply_count = len(pickings) if pickings else 0

    def button_confirm(self):
        _self = self.with_context(resupply_message_post=True)
        return super(PurchaseOrder, _self).button_confirm()

    def _message_track_post_template(self, changes):
        """We need to override this function with the previously used context
        so that the message appears after mail.tracking record (state = purchase)."""
        res = super()._message_track_post_template(changes)
        if self.env.context.get("resupply_message_post") and changes == {"state"}:
            self._resupply_message_post()
        return res

    def _resupply_message_post(self):
        for order in self:
            for picking in order.subcontracting_resupply_ids:
                body = _(
                    "This is for supplying raw material for "
                    "<a href=# data-oe-model=%(model)s data-oe-id=%(id)s>%(name)s</a>"
                ) % {"id": order.id, "name": order.name, "model": order._name}
                picking.with_user(SUPERUSER_ID).message_post(body=body)
                # purchase order message
                body = _(
                    "The resupply picking "
                    "<a href=# data-oe-model=%(model)s data-oe-id=%(id)s>%(name)s</a>"
                    " has been created"
                ) % {"id": picking.id, "name": picking.name, "model": picking._name}
                order.with_user(SUPERUSER_ID).message_post(body=body)

    def action_view_subcontracting_resupply(self):
        action = self.env.ref("stock.action_picking_tree_all").sudo().read()[0]
        picking_ids = self.mapped("subcontracting_resupply_ids")
        if len(picking_ids) > 1:
            action["domain"] = [("id", "in", picking_ids.ids)]
        else:
            action.update(
                res_id=picking_ids.id,
                view_mode="form",
                view_id=False,
                views=False,
            )
        return action
