from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _inherits = {
        "input.config": "input_config_id",
    }

    input_config_id = fields.Many2one(
        comodel_name="input.config",
        recursive="True",
    )

    def open_input_line_wizard(self):
        self.ensure_one()
        self.input_config_id.open_input_line_wizard()
