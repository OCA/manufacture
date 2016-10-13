# -*- coding: utf-8 -*-
# © 2015 AvanzOSC
# © 2015 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    @api.multi
    def write(self, vals):
        production_obj = self.env['mrp.production']
        if vals.get('production_id'):
            production = production_obj.browse(vals['production_id'])
            production.no_confirm = True
        return super(ProcurementOrder, self).write(vals)

    @api.multi
    def make_mo(self):
        res = super(ProcurementOrder, self).make_mo()
        for procurement in self:
            if (procurement.production_id and
                    procurement.production_id.no_confirm):
                procurement.production_id.no_confirm = False
        return res
