from odoo import api, fields, models


class InputConstraint(models.Model):
    _name = "input.constraint"
    _inherit = ["mail.thread"]
    _rec_name = "bom_id"
    _description = "Contains input data constraints"

    bom_id = fields.Many2one(comodel_name="mrp.bom")
    bom_domain = fields.Binary(compute="_compute_bom_domain")

    @api.depends("bom_id")
    def _compute_bom_domain(self):
        domain = self.env["mrp.bom"]._get_bom_domain_for_config()
        boms = self.env["mrp.bom"].search(domain)
        for rec in self:
            ids = boms and boms.ids or [False]
            rec.bom_domain = [("id", "in", ids)]
