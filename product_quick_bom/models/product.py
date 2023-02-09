#   Copyright (C) 2015 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends("bom_ids")
    def _compute_bom_id(self):
        for rec in self:
            if len(rec.bom_ids.ids) == 1:
                rec.bom_id = rec.bom_ids[0]
            else:
                rec.bom_id = self.env["mrp.bom"]

    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Bill of Materials (quick access)",
        compute="_compute_bom_id",
        store=True,
    )

    # In case there is no bom_id yet, to simplify logic
    # we just add a button to create one
    def button_create_bom(self):
        self.ensure_one()
        vals = {"product_tmpl_id": self.id, "type": "normal"}
        self.env["mrp.bom"].create(vals)

    specific_bom_line_ids = fields.One2many(
        related="bom_id.bom_line_ids", readonly=False
    )
