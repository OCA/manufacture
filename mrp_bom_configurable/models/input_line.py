from odoo import api, fields, models


class Inputline(models.Model):
    _name = "input.line"
    _description = "Line configuration scenari"

    name = fields.Char()
    sequence = fields.Integer()
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        required=True,
    )
    config_id = fields.Many2one(comodel_name="input.config", required=True)
    count = fields.Integer(default=1)
    alert = fields.Text(help="Outside limit configuration is reported here")
    checked = fields.Boolean(
        compute="_compute_check",
        store=True,
        help="If checked, the configuration have been evaluate",
    )
    comment = fields.Text()

    def ui_clone(self):
        self.ensure_one()
        vals = {"name": "%s copy" % self.name}
        self.copy(vals)

    def ui_configure(self):
        # TODO
        pass

    @api.depends("bom_id", "count")
    def _compute_check(self):
        "You need to override this method in your custom config to trigger adhoc checks"
