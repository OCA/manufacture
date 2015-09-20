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

from . import models
from openerp import SUPERUSER_ID, api


def uninstall_hook(cr, registry):
    """Restore workflow condition."""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        transition = env.ref('mrp.prod_trans_draft_picking')
        transition.condition = True
