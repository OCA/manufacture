# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Add precision
    produce_delay = fields.Float(
        digits="Produce Delay in Days",
    )
    produce_delay_in_hour = fields.Float(
        default=0.0,
        help="Average lead time in hours to manufacture this Product.",
    )

    @api.onchange("produce_delay_in_hour")
    def _onchange_produce_delay_in_hour(self):
        self.produce_delay = self.produce_delay_in_hour / 24
