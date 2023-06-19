# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class MrpBom(models.Model):
    _name = "mrp.bom"
    _inherit = ["mrp.bom", "tier.validation"]
    _state_from = ["to_approve"]
    _state_to = ["approve"]

    _tier_validation_manual_config = False

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("to_approve", "To Approve"),
            ("approve", "Approved"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        index=True,
        copy=False,
        default="draft",
        tracking=True,
    )

    def button_draft(self):
        self.write({"state": "draft"})
        return True

    def button_to_approve(self):
        self.write({"state": "to_approve"})
        return True

    def button_approve(self):
        self.write({"state": "approve"})
        return True

    def button_cancel(self):
        self.write({"state": "cancel"})
        return True
