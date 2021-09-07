# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class RepairOrder(models.Model):
    _inherit = "repair.order"

    vendor_id = fields.Many2one(
        "res.partner",
        string="Vendor",
        domain="['|', ('company_id', '=', False), " "('company_id', '=', company_id)]",
        help="You can find a vendor by its Name, TIN, " "Email or Internal Reference.",
    )

    vendor_refund_ids = fields.One2many(
        comodel_name="account.move", compute="_compute_vendor_refunds"
    )

    vendor_refund_count = fields.Integer(
        compute="_compute_vendor_refunds", string="# of Vendor Refunds"
    )
    vendor_refund_state = fields.Selection(
        [
            ("no", "Nothing to Refund"),
            ("to_refund", "Waiting Refunds"),
            ("refunded", "Fully Refunded"),
        ],
        string="Vendor Refund Status",
        compute="_compute_vendor_refund_state",
        store=True,
        readonly=True,
        copy=False,
        default="no",
    )

    @api.depends(
        "fees_lines.vendor_refund_pending_qty", "operations.vendor_refund_pending_qty"
    )
    def _compute_vendor_refund_state(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for rec in self:
            open_qty_to_refund_in_fees = any(
                not float_is_zero(
                    fee_line.vendor_refund_pending_qty, precision_digits=precision
                )
                for fee_line in rec.fees_lines
            )
            no_qty_to_refund_in_fees = (
                all(
                    float_is_zero(
                        fee_line.vendor_refund_pending_qty, precision_digits=precision
                    )
                    and not float_is_zero(
                        fee_line.vendor_to_refund_qty, precision_digits=precision
                    )
                    for fee_line in rec.fees_lines
                )
                and rec.fees_lines
            )
            open_qty_to_refund_in_operations = any(
                not float_is_zero(
                    operation.vendor_refund_pending_qty, precision_digits=precision
                )
                for operation in rec.operations
            )
            no_qty_to_refund_in_operations = (
                all(
                    float_is_zero(
                        operation.vendor_refund_pending_qty, precision_digits=precision
                    )
                    and not float_is_zero(
                        operation.vendor_to_refund_qty, precision_digits=precision
                    )
                    for operation in rec.operations
                )
                and rec.operations
            )
            if open_qty_to_refund_in_fees or open_qty_to_refund_in_operations:
                rec.vendor_refund_state = "to_refund"
            elif no_qty_to_refund_in_fees and no_qty_to_refund_in_operations:
                rec.vendor_refund_state = "refunded"
            else:
                rec.vendor_refund_state = "no"

    def _compute_vendor_refunds(self):
        for rec in self:
            refunds = rec.operations.mapped("vendor_refund_move_line_ids.move_id")
            refunds |= rec.fees_lines.mapped("vendor_refund_move_line_ids.move_id")
            rec.vendor_refund_ids = refunds
            rec.vendor_refund_count = len(refunds)

    def action_view_vendor_refund(self):
        move_ids = self.mapped("vendor_refund_ids").ids
        form_view_ref = self.env.ref("account.view_move_form", False)
        tree_view_ref = self.env.ref("account.view_in_invoice_tree", False)

        return {
            "domain": [("id", "in", move_ids)],
            "name": "Vendor Refunds",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "views": [(tree_view_ref.id, "tree"), (form_view_ref.id, "form")],
        }

    def _prepare_bill(self):
        """Prepare the dict of values to create the new invoice for a purchase order."""
        self.ensure_one()
        move_type = self._context.get("default_move_type", "in_invoice")
        journal = (
            self.env["account.move"]
            .with_context(default_move_type=move_type)
            ._get_default_journal()
        )
        if not journal:
            raise UserError(
                _(
                    "Please define an accounting purchase journal for the company %s (%s)."
                )
                % (self.company_id.name, self.company_id.id)
            )
        if not self.vendor_id:
            raise UserError(_("Please define a vendor for repair %s.") % self.name)
        vendor_invoice_id = self.vendor_id.address_get(["invoice"])["invoice"]
        invoice_vals = {
            "ref": self.name or "",
            "move_type": move_type,
            "currency_id": self.currency_id.id,
            "partner_id": vendor_invoice_id,
            "fiscal_position_id": (
                self.env["account.fiscal.position"].get_fiscal_position(
                    vendor_invoice_id
                )
            ).id,
            "partner_bank_id": self.vendor_id.bank_ids[:1].id,
            "invoice_origin": self.name,
            "invoice_line_ids": [],
            "company_id": self.company_id.id,
        }
        return invoice_vals
