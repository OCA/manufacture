# -*- coding: utf-8 -*-
# (c) 2016 Daniel Dico <dd@oerp.ca>
# (c) 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class HrAnalyticTimesheet(models.Model):
    _inherit = "hr.analytic.timesheet"

    @api.model
    def create(self, vals):
        production = self.env.context.get('production', False)
        workorder = self.env.context.get('workorder', False)
        vals['mrp_production_id'] = vals.get(
            'mrp_production_id', False) or production and production.id
        vals['workorder'] = vals.get(
            'workorder', False) or workorder and workorder.id
        return super(HrAnalyticTimesheet, self).create(vals)
