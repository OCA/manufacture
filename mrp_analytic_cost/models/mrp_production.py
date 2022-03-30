# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def generate_analytic_lines(self):
        """Generate Analytic Lines for a MO"""
        return self.mapped("move_raw_ids").generate_mrp_raw_analytic_line()
