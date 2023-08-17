from odoo import fields, models


class InputConfig(models.Model):
    _name = "input.config"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Product configuration scenari"

    name = fields.Char(required=True)
    date = fields.Date(string="Shipping Date")
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
        ],
        default="draft",
        ondelete={"pending": "draft", "confirmed": "draft"},
    )
    partner_id = fields.Many2one(comodel_name="res.partner")
    line_ids = fields.One2many(comodel_name="input.line", inverse_name="config_id")
