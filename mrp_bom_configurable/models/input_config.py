from odoo import fields, models


class InputConfig(models.Model):
    _name = "input.config"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Product configuration scenari"

    def _compute_bom_domain(self):
        var_boms = self.env["mrp.bom"].search([("configuration_type", "=", "variable")])
        var_tmpl = var_boms.mapped("product_tmpl_id")
        products = self.env["product.product"].search(
            [("product_tmpl_id", "in", var_tmpl.ids)]
        )
        compon_tmpl = (
            self.env["mrp.bom.line"]
            .search([("product_id", "=", products.ids)])
            .mapped("product_id.product_tmpl_id")
        )
        tmpls = var_tmpl - compon_tmpl
        boms = self.env["mrp.bom"].search(
            [
                ("configuration_type", "=", "variable"),
                ("product_tmpl_id", "in", tmpls.ids),
            ]
        )
        for rec in self:
            rec.bom_domain = [("id", "in", boms.ids)]

    name = fields.Char(required=True)
    date = fields.Date(default=fields.Date.today())
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Configurable Product",
        required=True,
        domain=_compute_bom_domain,
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

    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    def show_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Lines",
            "view_mode": "tree",
            "res_model": "input.line",
            "domain": [("config_id", "=", self.id)],
        }
