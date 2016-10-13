# -*- coding: utf-8 -*-
# © 2015 AvanzOSC
# © 2015 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from . import models
from openerp import SUPERUSER_ID, api


def uninstall_hook(cr, registry):
    """Restore workflow condition."""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        transition = env.ref('mrp.prod_trans_draft_picking')
        transition.condition = True
