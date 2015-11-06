# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Andrea Gallina
#    Copyright 2015 Apulia Software srl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api
from openerp.exceptions import Warning


class WizardHierarchy(models.TransientModel):

    _name = 'wizard.hierarchy'

    @api.multi
    def show_production_hierarchy(self):
        model = self.env.context.get('active_model', False)
        mo_id = self.env.context.get('active_id', False)
        if not model or not id:
            raise Warning('Select at least one MO')
        recset = self.env[model].browse(mo_id)
        res = self.env['mrp.production']._get_master_production(recset)
        action = self.env.ref(
            '{module}.{id}'.format(
                module='mrp_production_hierarchy',
                id='mrp_production_hierarchy_action'))
        result = action.read()[0]
        result['domain'] = "[('id', 'in', [{}])]".format(res.id)
        result['res_id'] = res.id
        return result
