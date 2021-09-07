# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMoveLine(models.Model):
    """Override AccountInvoice_line to add the link to the
    repair order line it is related to"""

    _inherit = "account.move.line"

    repair_line_id = fields.Many2one(
        "repair.line", "Repair Line", ondelete="set null", index=True
    )
    repair_fee_id = fields.Many2one(
        "repair.fee", "Repair Fee", ondelete="set null", index=True
    )
    repair_id = fields.Many2one("repair.order", compute="_compute_repair_id")

    def _compute_repair_id(self):
        for rec in self:
            if rec.repair_line_id:
                rec.repair_id = rec.repair_line_id.repair_id
            elif rec.repair_fee_id:
                rec.repair_id = rec.repair_fee_id.repair_id
            else:
                rec.repair_id = self.env["repair.order"]

    def _copy_data_extend_business_fields(self, values):
        # OVERRIDE to copy the 'purchase_line_id' field as well.
        super(AccountMoveLine, self)._copy_data_extend_business_fields(values)
        values["repair_line_id"] = self.repair_line_id.id
        values["repair_fee_id"] = self.repair_fee_id.id

    def _get_computed_account(self):
        # We do not want to use anglo saxon goods received not invoice
        # account in this case because we are not really sending the goods back.
        self.ensure_one()
        self = self.with_company(self.move_id.journal_id.company_id)
        fiscal_position = self.move_id.fiscal_position_id
        accounts = self.product_id.product_tmpl_id.get_product_accounts(
            fiscal_pos=fiscal_position
        )
        if self.repair_line_id and self.move_id.is_purchase_document(
            include_receipts=True
        ):
            return accounts["expense"]
        return super(AccountMoveLine, self)._get_computed_account()
