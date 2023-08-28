from odoo import fields, models


class Inputline(models.Model):
    _name = "input.line"
    _description = "Input data for bom configuration"

    name = fields.Char(required=True)
    sequence = fields.Integer()
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        required=True,
    )
    config_id = fields.Many2one(comodel_name="input.config", required=True)
    count = fields.Integer(default=1)
    comment = fields.Char()

    def ui_clone(self):
        self.ensure_one()
        vals = {"name": "%s copy" % self.name}
        self.copy(vals)

    def ui_configure(self):
        # TODO
        pass
