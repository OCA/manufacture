# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

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
