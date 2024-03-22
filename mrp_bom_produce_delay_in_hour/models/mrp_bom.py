# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    produce_delay_in_hour = fields.Float(
        compute="_compute_produce_delay_in_hour",
        inverse="_inverse_produce_delay_in_hour",
        help="Average lead time in hours to manufacture this Bill Of Material. "
        "Changes here will affect Product Produce Delay.",
    )

    @api.depends("product_tmpl_id.produce_delay_in_hour")
    def _compute_produce_delay_in_hour(self):
        for record in self:
            record.produce_delay_in_hour = record.product_tmpl_id.produce_delay_in_hour

    def _inverse_produce_delay_in_hour(self):
        for record in self:
            record.product_tmpl_id.produce_delay_in_hour = record.produce_delay_in_hour
            record.product_tmpl_id._onchange_produce_delay_in_hour()
