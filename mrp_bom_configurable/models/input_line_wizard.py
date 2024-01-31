from odoo import api, fields, models


class LineConfiguratorWizard(models.TransientModel):
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
        self.ensure_one()
        self.env["input.line"].create(
            {
                "bom_id": self.config_id.bom_id.id,
                "config_id": self.config_id.id,
                "name": self.name,
                "larg": self.larg,
                "haut": self.haut,
                "manoeuvre": self.manoeuvre,
                "lg_man": self.lg_man,
                "protocol": self.protocol,
                "cmvi": self.cmvi,
                "pose": self.pose,
                "coffre": self.coffre.id,
                "guidage": self.guidage,
                "sortie": self.sortie,
                "raid": self.raid,
            }
        )
