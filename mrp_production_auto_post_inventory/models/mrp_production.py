# © 2017 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    to_post_inventory_cron = fields.Boolean(
        string="To Post-Inventory by Job",
        track_visibility="onchange",
        help="Checked if configured in settings to auto post-inventory by scheduler. "
        "Unchecked when post-inventory is done",
    )

    @api.multi
    def post_inventory(self):
        res = super().post_inventory()
        self.write({"to_post_inventory_cron": False})
        return res

    @api.model
    def _cron_post_inventory(self, limit=1000):
        """ This method is called from a cron job. """
        records = self.search([("to_post_inventory_cron", "=", True)], limit=limit)
        records.post_inventory()
