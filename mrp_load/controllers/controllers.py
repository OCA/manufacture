# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers import main


class Action(main.Action):

    @http.route('/web/action/load', type='json', auth='user')
    def load(self, action_id, do_not_eval=False, additional_context=None):
        if 'mrp_load' in request.env.registry._init_modules:
            env = request.env
            try:
                action_id = int(action_id)
                mrp_action_id = env.ref('mrp.mrp_workcenter_action').id
                if action_id == mrp_action_id:
                    env['mrp.workcenter'].auto_recompute_load()
            except ValueError:
                raise
                if action_id == 'mrp.mrp_workcenter_action':
                    env['mrp.workcenter'].auto_recompute_load()
        return super(Action, self).load(
            action_id,
            do_not_eval=do_not_eval,
            additional_context=additional_context)
