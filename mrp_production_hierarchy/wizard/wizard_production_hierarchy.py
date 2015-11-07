# -*- coding: utf-8 -*-
#
# Author: Andrea Gallina
# ©  2015 Apulia Software srl
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
