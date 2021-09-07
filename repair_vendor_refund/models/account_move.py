# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    repair_id = fields.Many2one(
        "repair.order",
        store=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        string="Repair Order",
        help="Auto-complete from a past repair order.",
    )

    def _get_invoice_reference_from_repair(self):
        self.ensure_one()
        repairs = self.line_ids.mapped(
            "repair_line_id.repair_id"
        ) + self.line_ids.mapped("repair_fee_id.repair_id")
        repair_refs = [ref for ref in set(repairs.mapped("name")) if ref]
        if self.ref:
            return [
                ref for ref in self.ref.split(", ") if ref and ref not in repair_refs
            ] + repair_refs
        return repair_refs

    @api.onchange("repair_id")
    def _onchange_repair_auto_complete(self):
        if not self.repair_id:
            return
        # Copy data from Repair Order
        invoice_vals = self.repair_id.with_company(
            self.repair_id.company_id
        )._prepare_bill()
        del invoice_vals["ref"]
        self.update(invoice_vals)
        # Copy repair lines.
        repair_lines = self.repair_id.operations - self.line_ids.mapped(
            "repair_line_id"
        )
        new_lines = self.env["account.move.line"]
        for line in repair_lines.filtered(lambda l: not l.type == "remove"):
            new_line = new_lines.new(line._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        fee_lines = self.repair_id.fees_lines - self.line_ids.mapped("repair_fee_id")
        for fee in fee_lines:
            new_line = new_lines.new(fee._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()

        # Compute invoice_origin.
        origins = set(self.line_ids.mapped("repair_line_id.repair_id.name"))
        origins |= set(self.line_ids.mapped("repair_fee_id.repair_id.name"))
        self.invoice_origin = ",".join(list(origins))
        # Compute ref.
        refs = self._get_invoice_reference_from_repair()
        self.ref = ", ".join(refs)
        self.repair_id = False
        self._onchange_currency()
        self.partner_bank_id = (
            self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]
        )

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            if move.reversed_entry_id:
                continue
            repair = move.line_ids.mapped("repair_line_id.repair_id")
            repair |= move.line_ids.mapped("repair_fee_id.repair_id")
            if not repair:
                continue
            refs = [
                "<a href=# data-oe-model=repair.order "
                "data-oe-id=%s>%s</a>" % tuple(name_get)
                for name_get in repair.name_get()
            ]
            message = _("This vendor bill has been created from: %s") % ",".join(refs)
            move.message_post(body=message)
        return moves

    def write(self, vals):
        # OVERRIDE
        old_repairs = self.mapped("line_ids.repair_line_id.repair_id")
        old_repairs |= self.mapped("line_ids.repair_fee_id.repair_id")
        res = super(AccountMove, self).write(vals)
        for i, move in enumerate(self):
            new_repairs = move.mapped("line_ids.repair_line_id.repair_id")
            new_repairs |= move.mapped("line_ids.repair_fee_id.repair_id")
            if not new_repairs:
                continue
            diff_repairs = new_repairs - old_repairs[i]
            if diff_repairs:
                refs = [
                    "<a href=# data-oe-model=repair.order data-oe-id=%s>%s</a>"
                    % tuple(name_get)
                    for name_get in diff_repairs.name_get()
                ]
                message = _("This vendor bill has been modified from: %s") % ",".join(
                    refs
                )
                move.message_post(body=message)
        return res
