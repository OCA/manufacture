# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import _, api, fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    invoice_ids = fields.Many2many(
        "account.move",
        string="Invoices",
        copy=False,
        readonly=True,
        tracking=True,
        domain=[("move_type", "in", ("out_invoice", "out_refund"))],
    )

    invoiced = fields.Boolean(compute="_compute_invoiced", store=True)

    invoice_count = fields.Integer(
        compute="_compute_invoice_count",
        string="Bill Count",
        copy=False,
        default=0,
        store=True,
    )

    @api.depends("invoice_id.payment_state", "invoice_id")
    def _compute_invoiced(self):
        for repair in self:
            if repair.invoice_id.payment_state == "reversed":
                repair.invoiced = False
                repair.invoice_id = False
                repair.mapped("operations").filtered(lambda op: op.type == "add").write(
                    {"invoiced": False}
                )
                repair.mapped("fees_lines").write({"invoiced": False})
                repair.state = "2binvoiced"
            elif repair.invoice_id:
                repair.invoiced = True
            else:
                repair.invoiced = False

    @api.depends("invoice_ids")
    def _compute_invoice_count(self):
        for repair in self:
            repair.invoice_count = len(repair.invoice_ids)

    def _create_invoices(self, group=False):
        repair_dict = super()._create_invoices(group)
        for repair_id in repair_dict:
            repair = self.env["repair.order"].browse(repair_id)
            repair.invoice_ids += repair.invoice_id

    def action_created_invoices(self):
        self.ensure_one()
        action = {
            "name": _("Invoices created"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
        }

        if len(self.invoice_ids) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "view_id": self.env.ref("account.view_move_form").id,
                    "target": "current",
                    "res_id": self.invoice_ids.id,
                }
            )
        else:
            action.update(
                {
                    "view_mode": "tree,form",
                    "res_model": "account.move",
                    "domain": [("id", "in", self.invoice_ids.ids)],
                }
            )

        return action
