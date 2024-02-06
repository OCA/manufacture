import json

from odoo import api, fields, models


class InputConfig(models.Model):
    _name = "input.config"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Header configuration scenari"

    name = fields.Char(required=True)
    date = fields.Date(default=fields.Date.today())
    bom_id = fields.Many2one(
        comodel_name="mrp.bom", string="Configurable Product", required=True
    )
    bom_domain = fields.Binary(compute="_compute_bom_domain")
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
        ],
        default="draft",
        ondelete={"pending": "draft", "confirmed": "draft"},
    )
    sale_id = fields.Many2one(comodel_name="sale.order")
    partner_id = fields.Many2one(
        comodel_name="res.partner", related="sale_id.partner_id.commercial_partner_id"
    )
    line_ids = fields.One2many(comodel_name="input.line", inverse_name="config_id")
    line_count = fields.Integer(string="Lines", compute="_compute_line_count")

    @api.depends("bom_id")
    def _compute_bom_domain(self):
        domain = self.env["mrp.bom"]._get_bom_domain_for_config()
        boms = self.env["mrp.bom"].search(domain)
        for rec in self:
            ids = boms and boms.ids or [False]
            rec.bom_domain = [("id", "in", ids)]

    def _get_bom_domain(self):
        return [("configuration_type", "=", "variable")]

    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    def create_boms_from_config(self):
        for rec in self:
            for line in rec.line_ids:
                line.create_bom_from_line()

    def _get_wizard_context(self):
        return {
            "active_id": self.id,
        }

    def open_input_line_wizard(self):
        self.ensure_one()
        view = self.env.ref("mrp_bom_configurable.input_line_form_wizard_action")
        view.context = json.dumps(self._get_wizard_context())
        return view.read()[0]

    def show_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Lines",
            "view_mode": "tree",
            "res_model": "input.line",
            "domain": [("config_id", "=", self.id)],
        }
