# Copyright (C) 2017 Akretion (http://www.akretion.com). All Rights Reserved
# @author Florian DA COSTA <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_progress(self):
        self.write(
            {
                "state": "progress",
                "date_start": datetime.now(),
            }
        )
        return True

    def action_unstart(self):
        self.write(
            {
                "state": "confirmed",
                "date_start": False,
            }
        )
        return True
