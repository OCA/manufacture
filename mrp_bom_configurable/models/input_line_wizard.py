from odoo import api, fields, models


class InputLineWizard(models.TransientModel):
    _name = "input.line.wizard"
    _inherit = ["input.line"]
    _description = "Wizard model for input line"

    config_id = fields.Many2one(
        comodel_name="input.config",
        name="Produit configuré",
        required=True,
        ondelete="cascade",
        default=lambda self: self._default_project_id(),
    )

    @api.model
    def _default_project_id(self):
        return self.env.context.get("active_id")

    def create_input_line_and_bom(self):
        raise NotImplementedError("Should be implemented by specialization")
