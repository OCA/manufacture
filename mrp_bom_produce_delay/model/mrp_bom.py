# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    produce_delay = fields.Float(
        compute="_compute_produce_delay",
        inverse="_inverse_produce_delay",
        help="Average lead time in days to manufacture this Bill Of Material. "
        "Changes here will affect Product Produce Delay.",
    )

    @api.depends("product_tmpl_id.produce_delay")
    def _compute_produce_delay(self):
        for record in self:
            record.produce_delay = record.product_tmpl_id.produce_delay

    def _inverse_produce_delay(self):
        for record in self:
            record.product_tmpl_id.produce_delay = record.produce_delay
