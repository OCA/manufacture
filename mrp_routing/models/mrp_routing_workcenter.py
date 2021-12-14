# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models

from .mrp_routing_workcenter_template import FIELDS_TO_SYNC


class MrpRoutingWorkcenter(models.Model):

    _inherit = "mrp.routing.workcenter"

    template_id = fields.Many2one(
        comodel_name="mrp.routing.workcenter.template",
        string="Template",
        readonly=False,
    )

    on_template_change = fields.Selection(
        string="On template change?",
        selection=[
            ("nothing", "Do nothing"),
            ("sync", "Sync"),
        ],
        required=False,
        default="sync",
    )

    @api.onchange("template_id")
    def onchange_template_id(self):
        if self.template_id:
            to_update_data = self.template_id.read(
                FIELDS_TO_SYNC, load="_classic_wirte"
            )[0]
            to_update_data.pop("id")
            self.update(to_update_data)
