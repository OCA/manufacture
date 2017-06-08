# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    @api.model
    def make_mo(self):
        production_obj = self.env['mrp.production']
        res = super(ProcurementOrder, self).make_mo()
        for key in res.keys():
            production_id = res[key]
            production = production_obj.browse(production_id)
            if production.move_prod_id:
                saleline = production.move_prod_id.procurement_id.sale_line_id
                vals = {'sale_line': saleline.id}
                production.write(vals)
        return res
