# -*- coding: utf-8 -*-
# (c) 2016 Daniel Dico <dd@oerp.ca>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class HrAnalyticTimesheet(models.Model):
    _inherit = "hr.analytic.timesheet"

    @api.model
    def create(self, vals):
        production = self._context.get('production', False)
        vals['mrp_production_id'] = vals.get(
            'mrp_production_id', False) or production and production.id
        return super(HrAnalyticTimesheet, self).create(vals)
